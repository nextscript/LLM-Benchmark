"""
llama-server Client: Communication with the OpenAI-compatible llama-server.
"""

import json
import re
import time
import logging
from pathlib import PurePath
import requests
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)

DEFAULT_SERVER_URL = "http://127.0.0.1:8080"
DEFAULT_TIMEOUT = 600
_live_slot_snapshots: dict[str, tuple[int, float]] = {}

# Tags used by various reasoning chat templates to delimit model "thinking".
# Open and close variants must stay aligned by index.
_THINK_OPEN_TAGS = (
    "<think>",
    "<thinking>",
    "<reasoning>",
    "<reasoning_content>",
    "<|thinking|>",
    "<thought>",
    "<|begin_of_thought|>",
)
_THINK_CLOSE_TAGS = (
    "</think>",
    "</thinking>",
    "</reasoning>",
    "</reasoning_content>",
    "<|/thinking|>",
    "</thought>",
    "<|end_of_thought|>",
)
# Build one regex that matches any tag, keep group(1) as the matched tag.
_THINK_TAG_RE = re.compile(
    "|".join(re.escape(t) for t in (*_THINK_OPEN_TAGS, *_THINK_CLOSE_TAGS)),
    re.DOTALL,
)
_TAG_TO_OPENS = {t: "open" for t in _THINK_OPEN_TAGS}
_TAG_TO_OPENS.update({t: "close" for t in _THINK_CLOSE_TAGS})


def _split_chunk_by_thinking(chunk: str, in_thinking: bool):
    """Split a content chunk into (kind, text) pairs based on reasoning tags.

    Returns (list_of_pairs, new_in_thinking_state). Tags that span two chunks
    are handled by returning the unmatched tail as plain text of the current
    kind (rare in practice).
    """
    parts: list[tuple[str, str]] = []
    pos = 0
    while pos < len(chunk):
        m = _THINK_TAG_RE.search(chunk, pos)
        if not m:
            parts.append(("thinking" if in_thinking else "content", chunk[pos:]))
            break
        if m.start() > pos:
            parts.append(("thinking" if in_thinking else "content", chunk[pos:m.start()]))
        tag = m.group(0)
        if _TAG_TO_OPENS.get(tag) == "open":
            in_thinking = True
        elif _TAG_TO_OPENS.get(tag) == "close":
            in_thinking = False
        else:
            # DeepSeek-style "tidi" tag toggles both states; flip
            in_thinking = not in_thinking
        pos = m.end()
    return parts, in_thinking


def _detect_repetition(content: str, min_unit_len: int = 16, min_repeats: int = 4) -> bool:
    """Return True if the tail of `content` shows an obvious repetition loop.

    Looks for a unit of length [min_unit_len .. 4*min_unit_len] that repeats at
    least `min_repeats` times back-to-back at the end of the string.
    """
    if not content:
        return False
    needed = min_unit_len * min_repeats
    if len(content) < needed:
        return False

    max_unit_len = min(min_unit_len * 32, len(content) // min_repeats)
    for unit_len in range(min_unit_len, max_unit_len + 1):
        unit = content[-unit_len:]
        if not unit.strip():
            continue
        count = 1
        i = len(content) - unit_len
        while i - unit_len >= 0 and content[i - unit_len:i] == unit:
            count += 1
            i -= unit_len
            if count >= min_repeats:
                return True
    return False


def _strip_thinking_tags(content: str) -> tuple[str, str]:
    """Remove thinking blocks from content and return (clean_content, thinking).

    Used for non-streaming responses where reasoning tags are embedded directly
    in the content string.
    """
    if not content:
        return content, ""
    thinking_parts: list[str] = []
    clean_parts: list[str] = []
    in_thinking = False
    pos = 0
    while pos < len(content):
        m = _THINK_TAG_RE.search(content, pos)
        if not m:
            (thinking_parts if in_thinking else clean_parts).append(content[pos:])
            break
        if m.start() > pos:
            (thinking_parts if in_thinking else clean_parts).append(content[pos:m.start()])
        tag = m.group(0)
        if _TAG_TO_OPENS.get(tag) == "open":
            in_thinking = True
        elif _TAG_TO_OPENS.get(tag) == "close":
            in_thinking = False
        else:
            in_thinking = not in_thinking
        pos = m.end()
    return "".join(clean_parts), "".join(thinking_parts)


def check_health(server_url: str, timeout: int = 10) -> bool:
    """Check if the llama-server is reachable."""
    try:
        resp = requests.get(f"{server_url}/health", timeout=timeout)
        return resp.status_code == 200
    except requests.exceptions.ConnectionError:
        logger.warning("llama-server not reachable at %s", server_url)
        return False
    except requests.exceptions.Timeout:
        logger.warning("Timeout during connection test to %s", server_url)
        return False
    except Exception as e:
        logger.error("Error during connection test: %s", e)
        return False


def _parse_sse_stream(resp) -> list[dict]:
    """Yield parsed JSON events from a text/event-stream response."""
    buffer = ""
    for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
        if not chunk:
            continue
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line or not line.startswith("data:"):
                continue
            data_str = line[5:].strip()
            if data_str == "[DONE]":
                continue
            try:
                yield json.loads(data_str)
            except json.JSONDecodeError:
                continue


def send_completion(server_url: str, prompt: str, model_name: str = "benchmark-model",
                    context_size: int = 4096, max_tokens: int = 512,
                    temperature: float = 0.7, top_p: float = 0.9,
                    timeout: int = DEFAULT_TIMEOUT,
                    on_token: Optional[Callable[[str, str], None]] = None) -> Optional[Dict[str, Any]]:
    """
    Send a prompt to the llama-server and return the response with metadata.

    When `on_token(kind, text)` is provided, the request is streamed via SSE and each
    generated chunk is forwarded live to the callback. `kind` is one of
    "thinking" (reasoning_content, when present) or "content" (final answer).

    Returns None if the server does not respond.
    """
    payload = {
        "model": model_name,
        "prompt": prompt,
        "n_predict": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "n_ctx": context_size,
        "cache_prompt": True,
    }

    try:
        logger.info("Sending prompt to %s (model: %s)", server_url, model_name)
        start_time = time.perf_counter()

        if on_token is not None:
            # ── Streaming mode ──
            payload["stream"] = True
            content_parts: list[str] = []
            thinking_parts: list[str] = []
            timings: dict = {}
            completion_tokens = 0
            prompt_tokens = 0

            with requests.post(
                f"{server_url}/completion",
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"},
                stream=True,
            ) as resp:
                if resp.status_code != 200:
                    logger.error("Server response error %d: %s", resp.status_code, resp.text[:500])
                    return None
                in_thinking = False
                for event in _parse_sse_stream(resp):
                    if not isinstance(event, dict):
                        continue
                    raw = event.get("content") or event.get("completion") or ""
                    if raw:
                        content_parts.append(raw)
                        # Split into thinking/content based on reasoning tags
                        parts, in_thinking = _split_chunk_by_thinking(raw, in_thinking)
                        for kind, text in parts:
                            if text:
                                on_token(kind, text)
                                if kind == "thinking":
                                    thinking_parts.append(text)
                    if "timings" in event:
                        timings = event.get("timings", {}) or {}
                    if "tokens_predicted" in event:
                        completion_tokens = event.get("tokens_predicted", completion_tokens)
                    if "tokens_evaluated" in event:
                        prompt_tokens = event.get("tokens_evaluated", prompt_tokens)
                    # Repetition loop detection: abort early if the model is stuck
                    if _detect_repetition("".join(content_parts)):
                        on_token("status", "[repetition loop detected, stopping stream]")
                        break

            elapsed = time.perf_counter() - start_time
            on_token("status", f"[stream complete: {elapsed:.2f}s]")
            content = "".join(content_parts)
            thinking = "".join(thinking_parts)
            return _build_result(timings, content, prompt_tokens, completion_tokens, elapsed, thinking)
        else:
            payload["stream"] = False
            resp = requests.post(
                f"{server_url}/completion",
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )

            elapsed = time.perf_counter() - start_time

            if resp.status_code != 200:
                logger.error("Server response error %d: %s", resp.status_code, resp.text[:500])
                return None

            data = resp.json()
            logger.debug("Server response keys: %s", list(data.keys()))
            logger.debug("Timings: %s", data.get("timings", {}))

            raw_content = data.get("content", "")
            content, thinking = _strip_thinking_tags(raw_content)

            return _build_result(
                data.get("timings", {}),
                content,
                data.get("tokens_evaluated", 0),
                data.get("tokens_predicted", 0),
                elapsed,
                thinking,
            )
    except requests.exceptions.ConnectionError:
        logger.error("Connection to server failed: %s", server_url)
        return None
    except requests.exceptions.Timeout:
        logger.error("Timeout sending to %s", server_url)
        return None
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return None


def _build_result(timings: dict, content: str, prompt_tokens_fallback: int,
                  completion_tokens_fallback: int, elapsed: float,
                  thinking: str = "") -> Dict[str, Any]:
    """Build the normalized result dict from raw server data."""
    prompt_tokens = (
        timings.get("prompt_n")
        or timings.get("prompt_eval_count")
        or prompt_tokens_fallback
        or 0
    )

    completion_tokens = (
        timings.get("eval_count")
        or timings.get("predicted_n")
        or completion_tokens_fallback
        or 0
    )

    prompt_eval_duration_ns = (
        timings.get("prompt_eval_duration")
        or timings.get("prompt_ms", 0) * 1e6
        or 0
    )

    eval_duration_ns = (
        timings.get("eval_duration")
        or timings.get("predicted_ms", 0) * 1e6
        or 0
    )

    prompt_tps = prompt_tokens / (prompt_eval_duration_ns / 1e9) if prompt_eval_duration_ns > 0 else 0.0
    generation_tps = completion_tokens / (eval_duration_ns / 1e9) if eval_duration_ns > 0 else 0.0

    first_token_latency = None
    avg_token_latency = 0.0
    if completion_tokens > 0:
        generation_time_s = eval_duration_ns / 1e9 if eval_duration_ns > 0 else elapsed
        first_token_latency = (prompt_eval_duration_ns / 1e9) * 1000 if prompt_eval_duration_ns > 0 else elapsed * 1000
        avg_token_latency = (generation_time_s * 1000) / completion_tokens

    return {
        "content": content,
        "thinking": thinking,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "prompt_tokens_per_second": round(prompt_tps, 2),
        "generation_tokens_per_second": round(generation_tps, 2),
        "total_duration": elapsed,
        "first_token_latency": round(first_token_latency, 2) if first_token_latency else None,
        "avg_token_latency": round(avg_token_latency, 4),
    }


def _coerce_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _sampling_float(value: Any) -> Optional[float]:
    number = _coerce_float(value)
    if number is None:
        return None
    rounded = round(number, 6)
    return 0.0 if rounded == -0.0 else rounded


def _coerce_int(value: Any) -> Optional[int]:
    number = _coerce_float(value)
    return int(number) if number is not None else None


def _clean_model_name(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not value.strip():
        return None

    cleaned = PurePath(value.strip().replace("\\", "/")).name
    if cleaned.lower().endswith(".gguf"):
        cleaned = cleaned[:-5]
    return cleaned or None


def _first_present(data: Any, keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = _nested_value(data, key)
        if value is not None:
            return value
    return None


def _metric_value(metrics_text: str, names: tuple[str, ...]) -> Optional[float]:
    values: list[float] = []
    for raw_line in metrics_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or " " not in line:
            continue
        metric_name, raw_value = line.rsplit(None, 1)
        metric_base = metric_name.split("{", 1)[0]
        if metric_base in names:
            value = _coerce_float(raw_value)
            if value is not None:
                values.append(value)
    return sum(values) if values else None


def read_llama_metrics(server_url: str, timeout: int = 2) -> Dict[str, Optional[float]]:
    """Read Prometheus-style live metrics from llama-server."""
    result: Dict[str, Optional[float]] = {
        "tokens_per_second": None,
        "decoded_tokens": None,
    }

    try:
        resp = requests.get(f"{server_url}/metrics", timeout=timeout)
        if resp.status_code != 200:
            return result

        text = resp.text
        decoded = _metric_value(text, (
            "llamacpp:tokens_predicted_total",
            "llamacpp:predicted_tokens_total",
            "llama_tokens_predicted_total",
            "llama_predicted_tokens_total",
        ))
        tps = _metric_value(text, (
            "llamacpp:predicted_tokens_seconds",
            "llamacpp:tokens_predicted_seconds",
            "llamacpp:tokens_predicted_per_second",
            "llamacpp:predicted_tokens_per_second",
            "llama_tokens_predicted_per_second",
            "llama_predicted_tokens_per_second",
        ))

        result["decoded_tokens"] = int(decoded) if decoded is not None else None
        result["tokens_per_second"] = tps
    except Exception:
        logger.debug("llama-server /metrics unavailable", exc_info=True)

    return result


def read_llama_configuration(server_url: str, timeout: int = 3) -> Dict[str, Any]:
    """Read configuration defaults exposed by llama-server."""
    result: Dict[str, Any] = {
        "ok": False,
        "server_url": server_url,
        "model_name": None,
        "context_size": None,
        "max_tokens": None,
        "temperature": None,
        "top_p": None,
        "sources": [],
    }

    def merge_from_payload(payload: Any, source: str) -> None:
        if not isinstance(payload, (dict, list)):
            return

        model_name = _clean_model_name(_first_present(payload, (
            "model_name",
            "model",
            "model_path",
            "model_alias",
            "default_generation_settings.model",
        )))
        if model_name and not result["model_name"]:
            result["model_name"] = model_name

        context_size = _coerce_int(_first_present(payload, (
            "default_generation_settings.n_ctx",
            "default_generation_settings.n_ctx_train",
            "n_ctx",
            "n_ctx_train",
            "slots.n_ctx",
        )))
        if context_size is not None and result["context_size"] is None:
            result["context_size"] = context_size

        batch_size = _coerce_int(_first_present(payload, (
            "default_generation_settings.n_batch",
            "default_generation_settings.n_ubatch",
            "n_batch",
            "n_ubatch",
        )))
        if batch_size is not None and result["max_tokens"] is None:
            result["max_tokens"] = batch_size

        temperature = _sampling_float(_first_present(payload, (
            "default_generation_settings.params.temperature",
            "default_generation_settings.temperature",
            "params.temperature",
            "temperature",
            "temp",
        )))
        if temperature is not None and result["temperature"] is None:
            result["temperature"] = temperature

        top_p = _sampling_float(_first_present(payload, (
            "default_generation_settings.params.top_p",
            "default_generation_settings.top_p",
            "params.top_p",
            "top_p",
        )))
        if top_p is not None and result["top_p"] is None:
            result["top_p"] = top_p

        if source not in result["sources"]:
            result["sources"].append(source)

    try:
        resp = requests.get(f"{server_url}/props", timeout=timeout)
        if resp.status_code == 200:
            merge_from_payload(resp.json(), "props")
    except Exception:
        logger.debug("llama-server /props unavailable", exc_info=True)

    try:
        resp = requests.get(f"{server_url}/v1/models", timeout=timeout)
        if resp.status_code == 200:
            payload = resp.json()
            models = payload.get("data") if isinstance(payload, dict) else None
            if isinstance(models, list) and models:
                model = models[0]
                if isinstance(model, dict):
                    model_name = _clean_model_name(model.get("id") or model.get("name"))
                    if model_name and not result["model_name"]:
                        result["model_name"] = model_name
                    if "v1/models" not in result["sources"]:
                        result["sources"].append("v1/models")
    except Exception:
        logger.debug("llama-server /v1/models unavailable", exc_info=True)

    try:
        resp = requests.get(f"{server_url}/slots", timeout=timeout)
        if resp.status_code == 200:
            merge_from_payload({"slots": _extract_slot_payload(resp.json())}, "slots")
    except Exception:
        logger.debug("llama-server /slots unavailable", exc_info=True)

    result["ok"] = any(
        result[key] is not None
        for key in ("model_name", "context_size", "max_tokens", "temperature", "top_p")
    )
    return result


def _extract_slot_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [slot for slot in payload if isinstance(slot, dict)]
    if isinstance(payload, dict):
        slots = payload.get("slots")
        if isinstance(slots, list):
            return [slot for slot in slots if isinstance(slot, dict)]
        if isinstance(slots, dict):
            return [slot for slot in slots.values() if isinstance(slot, dict)]
        return [payload]
    return []


def _nested_value(data: Any, key: str) -> Any:
    def walk(value: Any, parts: list[str]) -> Any:
        if not parts:
            return value
        if isinstance(value, dict):
            return walk(value.get(parts[0]), parts[1:])
        if isinstance(value, list):
            values = [walk(item, parts) for item in value]
            values = [item for item in values if item is not None]
            if values and all(isinstance(item, (int, float)) for item in values):
                return sum(values)
            return values[0] if values else None
        return None

    return walk(data, key.split("."))


def _slot_nested_int(slot: dict[str, Any], *keys: str) -> Optional[int]:
    for key in keys:
        coerced = _coerce_int(_nested_value(slot, key))
        if coerced is not None:
            return coerced
    return None


def _slot_nested_float(slot: dict[str, Any], *keys: str) -> Optional[float]:
    for key in keys:
        coerced = _coerce_float(_nested_value(slot, key))
        if coerced is not None:
            return coerced
    return None


def read_llama_slots(server_url: str, timeout: int = 2) -> Dict[str, Any]:
    """Read live slot counters and derive tokens/s if needed."""
    result: Dict[str, Any] = {
        "tokens_per_second": None,
        "decoded_tokens": None,
        "active": False,
    }

    try:
        resp = requests.get(f"{server_url}/slots", timeout=timeout)
        if resp.status_code != 200:
            return result

        decoded_total = 0
        decoded_seen = False
        tps_values: list[float] = []

        for slot in _extract_slot_payload(resp.json()):
            state = str(slot.get("state") or slot.get("slot_state") or "").lower()
            is_active = bool(slot.get("is_processing") or slot.get("processing") or state in ("processing", "busy"))
            result["active"] = bool(result["active"] or is_active)
            decoded = _slot_nested_int(
                slot,
                "next_token.n_decoded",
                "n_decoded",
                "tokens_decoded",
                "tokens_predicted",
                "n_predict",
                "n_predicted",
            )
            if decoded is not None and (is_active or decoded > 0):
                decoded_total += decoded
                decoded_seen = True

            tps = _slot_nested_float(
                slot,
                "tokens_per_second",
                "generation_tokens_per_second",
                "predicted_tokens_per_second",
                "tokens_predicted_per_second",
                "tps",
            )
            if tps is not None and tps > 0:
                tps_values.append(tps)

        if decoded_seen:
            result["decoded_tokens"] = decoded_total
            result["tokens_per_second"] = sum(tps_values) if tps_values else None

            if result["tokens_per_second"] is None:
                now = time.monotonic()
                previous = _live_slot_snapshots.get(server_url)
                if previous:
                    prev_decoded, prev_time = previous
                    elapsed = now - prev_time
                    if elapsed > 0 and decoded_total >= prev_decoded:
                        result["tokens_per_second"] = (decoded_total - prev_decoded) / elapsed
                _live_slot_snapshots[server_url] = (decoded_total, now)
    except Exception:
        logger.debug("llama-server /slots metrics unavailable", exc_info=True)

    return result


def reset_live_llama_status(server_url: Optional[str] = None) -> None:
    """Clear live metric deltas so a new run starts from a clean baseline."""
    if server_url is None:
        _live_slot_snapshots.clear()
        return
    _live_slot_snapshots.pop(server_url, None)


def get_live_llama_status(server_url: str, timeout: int = 2) -> Dict[str, Any]:
    """Read live generation status, preferring /metrics over /slots."""
    metrics = read_llama_metrics(server_url, timeout=timeout)
    slots = read_llama_slots(server_url, timeout=timeout)

    if metrics.get("tokens_per_second") is not None:
        decoded = slots.get("decoded_tokens")
        decoded_source = "slots" if decoded is not None else "metrics"
        return {
            "ok": True,
            "tokens_per_second": metrics["tokens_per_second"],
            "decoded_tokens": decoded if decoded is not None else metrics.get("decoded_tokens"),
            "source": "metrics",
            "decoded_source": decoded_source,
            "active": bool(slots.get("active")),
        }

    if slots.get("decoded_tokens") is not None:
        return {
            "ok": True,
            "tokens_per_second": slots.get("tokens_per_second"),
            "decoded_tokens": slots.get("decoded_tokens"),
            "source": "slots",
            "decoded_source": "slots",
            "active": bool(slots.get("active")),
        }

    return {
        "ok": False,
        "tokens_per_second": None,
        "decoded_tokens": None,
        "source": "unavailable",
        "decoded_source": "unavailable",
        "active": False,
    }


def get_live_generation_metrics(server_url: str, timeout: int = 2) -> Dict[str, Any]:
    """Backward-compatible wrapper for live llama-server status."""
    return get_live_llama_status(server_url, timeout=timeout)


def send_chat_completion(server_url: str, messages: list, model_name: str = "benchmark-model",
                         context_size: int = 4096, max_tokens: int = 512,
                         temperature: float = 0.7, top_p: float = 0.9,
                         timeout: int = DEFAULT_TIMEOUT,
                         on_token: Optional[Callable[[str, str], None]] = None) -> Optional[Dict[str, Any]]:
    """
    Send a chat completion (OpenAI-compatible).

    When `on_token(kind, text)` is provided, the request is streamed via SSE and
    each generated chunk is forwarded live. `kind` is "thinking" (reasoning_content)
    or "content" (final answer).
    """
    payload = {
        "model": model_name,
        "messages": messages,
        "n_predict": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "n_ctx": context_size,
    }

    try:
        logger.info("Sending chat request to %s", server_url)
        start_time = time.perf_counter()

        if on_token is not None:
            # ── Streaming chat mode ──
            payload["stream"] = True
            payload["reasoning_format"] = "deepseek"
            content_parts: list[str] = []
            thinking_parts: list[str] = []
            usage: dict = {}
            timings: dict = {}

            with requests.post(
                f"{server_url}/v1/chat/completions",
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"},
                stream=True,
            ) as resp:
                if resp.status_code != 200:
                    logger.error("Chat API error %d: %s", resp.status_code, resp.text[:500])
                    return None
                for event in _parse_sse_stream(resp):
                    if not isinstance(event, dict):
                        continue
                    choices = event.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {}) if isinstance(choices[0], dict) else {}
                    if not isinstance(delta, dict):
                        delta = {}
                    rc = delta.get("reasoning_content") or delta.get("reasoning")
                    if rc:
                        thinking_parts.append(rc)
                        on_token("thinking", rc)
                    cc = delta.get("content")
                    if cc:
                        content_parts.append(cc)
                        on_token("content", cc)
                    if event.get("usage"):
                        usage = event.get("usage", {}) or {}
                    if event.get("timings"):
                        timings = event.get("timings", {}) or {}

            elapsed = time.perf_counter() - start_time
            on_token("status", f"[chat stream complete: {elapsed:.2f}s]")
            content = "".join(content_parts)
            thinking = "".join(thinking_parts)
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            if timings:
                p_n = timings.get("prompt_n", 0) or timings.get("prompt_eval_count", 0)
                e_c = timings.get("eval_count", 0) or timings.get("predicted_n", 0)
                if p_n > 0:
                    prompt_tokens = p_n
                if e_c > 0:
                    completion_tokens = e_c
            return _build_chat_result(content, thinking, prompt_tokens, completion_tokens, timings, elapsed)

        payload["stream"] = False
        resp = requests.post(
            f"{server_url}/v1/chat/completions",
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )

        elapsed = time.perf_counter() - start_time

        if resp.status_code != 200:
            logger.error("Chat API error %d: %s", resp.status_code, resp.text[:500])
            return None

        data = resp.json()
        message = data.get("choices", [{}])[0].get("message", {}) if data.get("choices") else {}
        content = message.get("content", "") if isinstance(message, dict) else ""
        thinking = message.get("reasoning_content", "") if isinstance(message, dict) else ""
        usage = data.get("usage", {})

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        timings = data.get("timings", {})
        return _build_chat_result(content, thinking, prompt_tokens, completion_tokens, timings, elapsed)

    except requests.exceptions.ConnectionError:
        logger.error("Connection to server failed: %s", server_url)
        return None
    except requests.exceptions.Timeout:
        logger.error("Timeout on chat request to %s", server_url)
        return None
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return None


def _build_chat_result(content: str, thinking: str, prompt_tokens: int,
                       completion_tokens: int, timings: dict, elapsed: float) -> Dict[str, Any]:
    """Build normalized result dict for chat completion responses."""
    total_tokens = prompt_tokens + completion_tokens
    prompt_tps = prompt_tokens / elapsed if elapsed > 0 else 0.0
    generation_tps = completion_tokens / elapsed if elapsed > 0 else 0.0
    avg_token_latency = (elapsed * 1000) / completion_tokens if completion_tokens > 0 else 0.0
    first_token_latency = None

    if timings:
        prompt_eval_ns = timings.get("prompt_eval_duration", 0) or timings.get("prompt_ms", 0) * 1e6
        eval_ns = timings.get("eval_duration", 0) or timings.get("predicted_ms", 0) * 1e6
        p_n = timings.get("prompt_n", 0) or timings.get("prompt_eval_count", 0)
        e_c = timings.get("eval_count", 0) or timings.get("predicted_n", 0)
        if p_n > 0:
            prompt_tokens = p_n
        if e_c > 0:
            completion_tokens = e_c
            total_tokens = prompt_tokens + completion_tokens
        if eval_ns > 0 and completion_tokens > 0:
            generation_tps = completion_tokens / (eval_ns / 1e9)
            avg_token_latency = (eval_ns / 1e6) / completion_tokens
        if prompt_eval_ns > 0:
            prompt_tps = prompt_tokens / (prompt_eval_ns / 1e9)
            first_token_latency = prompt_eval_ns / 1e6

    result = {
        "content": content,
        "thinking": thinking,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "prompt_tokens_per_second": round(prompt_tps, 2),
        "generation_tokens_per_second": round(generation_tps, 2),
        "total_duration": elapsed,
        "first_token_latency": round(first_token_latency, 2) if first_token_latency else None,
        "avg_token_latency": round(avg_token_latency, 4),
    }

    logger.info("Chat response: %d prompt tokens, %d generation tokens",
                 result["prompt_tokens"], result["completion_tokens"])

    return result


def get_system_metrics() -> Dict[str, Optional[float]]:
    """Determine RAM and VRAM usage."""
    import psutil
    import subprocess

    ram = psutil.virtual_memory()
    result = {
        "ram_usage_mb": round(ram.used / (1024 * 1024), 2),
        "vram_usage_mb": None,
    }

    # VRAM via nvidia-smi
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            timeout=5
        ).decode().strip()
        if output:
            result["vram_usage_mb"] = float(output.split("\n")[0])
    except (FileNotFoundError, subprocess.SubprocessError, ValueError):
        logger.debug("nvidia-smi not available or no VRAM measurable")

    return result
