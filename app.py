"""
Main App: FastAPI application for LLM benchmarking.
"""

import logging
import os
import threading

from fastapi import FastAPI, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from database import (
    init_db, migrate_db, create_model, get_all_models, create_run, update_run_status,
    get_run, get_active_run, create_result, get_all_results, get_result, delete_result,
    delete_result_run, update_quality_score, get_stats, get_language_badges_by_model, get_engine_badges_by_model
)
from benchmark import run_benchmark, PROMPTS, ENGINE_QUICK_TEST_SET
from llama_client import (
    check_health,
    get_live_llama_status,
    read_llama_configuration,
    reset_live_llama_status,
)

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/benchmark.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Benchmark status (running benchmarks)
active_benchmarks: dict = {}
abort_flags: dict = {}  # {run_id: True/False}
live_decoded_baselines: dict = {}

# In-memory log buffer for the active benchmark run (per run_id)
active_benchmark_logs: dict = {}
# In-memory live KI stream buffer: run_id -> list of {"kind": "thinking"|"content"|"status", "text": str}
active_benchmark_streams: dict = {}
_log_thread_local = threading.local()


class RunLogHandler(logging.Handler):
    """Captures log records emitted from the benchmark thread into active_benchmark_logs[run_id]."""

    def emit(self, record: logging.LogRecord) -> None:
        run_id = getattr(_log_thread_local, "run_id", None)
        if run_id is None:
            return
        try:
            line = self.format(record)
            buf = active_benchmark_logs.get(run_id)
            if buf is None:
                buf = []
                active_benchmark_logs[run_id] = buf
            buf.append(line)
            # Cap buffer to avoid unbounded growth
            if len(buf) > 5000:
                del buf[: len(buf) - 5000]
        except Exception:
            pass


_run_log_handler = RunLogHandler()
_run_log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
logging.getLogger().addHandler(_run_log_handler)

# App initialization
app = FastAPI(title="LLM Benchmark GUI", version="1.0.0")

# Template and static directories
templates = Jinja2Templates(directory="templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "sounds"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def parse_decimal_form_value(value: str | float | int, field_name: str, min_value: float, max_value: float) -> float:
    """Parse decimal form values that may use a comma as decimal separator."""
    try:
        parsed = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"{field_name} must be a decimal number.")

    if not (min_value <= parsed <= max_value):
        raise HTTPException(status_code=400, detail=f"{field_name} must be between {min_value} and {max_value}.")
    return parsed


# Startup
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    migrate_db()
    logger.info("Database initialized.")


# HTML Pages
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/benchmark", response_class=HTMLResponse)
async def benchmark_page(request: Request):
    default_server_url = os.environ.get("LLAMA_SERVER_URL", "http://127.0.0.1:8080")
    return templates.TemplateResponse(request, "benchmark.html", {"default_server_url": default_server_url})


@app.get("/results", response_class=HTMLResponse)
async def results_page(request: Request):
    return templates.TemplateResponse(request, "results.html")


@app.get("/ranking", response_class=HTMLResponse)
async def ranking_page(request: Request):
    return templates.TemplateResponse(request, "ranking.html")


@app.get("/comparisons", response_class=HTMLResponse)
async def comparisons_page(request: Request):
    return templates.TemplateResponse(request, "comparisons.html")


# API Endpoints
@app.get("/api/health")
async def health_check(server_url: str | None = Query(None)):
    """Check llama-server connection."""
    server_url = server_url or os.environ.get("LLAMA_SERVER_URL", "http://127.0.0.1:8080")
    reachable = check_health(server_url)
    return {"server_url": server_url, "reachable": reachable}


@app.get("/api/llama-config")
async def api_llama_config(server_url: str = Query("http://127.0.0.1:8080")):
    """Return configuration defaults exposed by llama-server."""
    return read_llama_configuration(server_url)


@app.get("/api/prompts")
async def get_prompts():
    """Return all available prompts with metadata."""
    return [
        {
            "key": k,
            "name": v.get("name", k),
            "category": v.get("category", "general"),
            "language": v.get("language"),
            "language_label": v.get("language_label"),
            "engine_skill": v.get("engine_skill"),
            "engine_skill_label": v.get("engine_skill_label"),
            "songwriting_skill": v.get("songwriting_skill"),
            "songwriting_skill_label": v.get("songwriting_skill_label"),
            "sub_category": v.get("sub_category"),
            "genre": v.get("genre"),
            "difficulty": v.get("difficulty", "medium"),
        }
        for k, v in PROMPTS.items()
    ]


@app.get("/api/prompts/engine-quick-test")
async def get_engine_quick_test():
    """Return the engine quick test set prompt keys."""
    return {"keys": ENGINE_QUICK_TEST_SET}


@app.get("/api/language-badges")
async def api_language_badges():
    """Return language badges grouped by model."""
    return get_language_badges_by_model()


@app.get("/api/engine-badges")
async def api_engine_badges():
    """Return engine skill badges grouped by model."""
    return get_engine_badges_by_model()


@app.post("/api/benchmark/start")
async def start_benchmark(
    model_name: str = Form(...),
    server_url: str = Form("http://127.0.0.1:8080"),
    context_size: int = Form(4096),
    num_runs: int = Form(1),
    prompt_keys: str = Form(""),
    max_tokens: int = Form(512),
    temperature: str = Form("0.7"),
    top_p: str = Form("0.9"),
    enable_self_validation: str = Form("true"),
):
    """Start a benchmark in the background."""
    if not model_name.strip():
        raise HTTPException(status_code=400, detail="Model name cannot be empty.")

    prompt_list = [p.strip() for p in prompt_keys.split(",") if p.strip()]
    if not prompt_list:
        prompt_list = list(PROMPTS.keys())

    use_self_validation = enable_self_validation.lower() in ("true", "1", "yes", "on")
    temperature_value = parse_decimal_form_value(temperature, "Temperature", 0, 2)
    top_p_value = parse_decimal_form_value(top_p, "Top-P", 0, 1)

    # Check server connection
    if not check_health(server_url):
        run_id = create_run(model_name, server_url)
        update_run_status(run_id, "failed", 0, "Server not reachable",
                          f"llama-server at {server_url} is not reachable.")
        return {"run_id": run_id, "status": "failed", "message": "Server not reachable."}

    # Create run
    run_id = create_run(model_name, server_url)
    live_decoded_baselines.pop(run_id, None)
    reset_live_llama_status(server_url)
    update_run_status(run_id, "running", 0, "Connecting to server...")

    # Background thread for benchmark
    def _run_benchmark():
        _log_thread_local.run_id = run_id
        active_benchmark_logs[run_id] = []
        active_benchmark_streams[run_id] = []

        def _on_token(kind: str, text: str) -> None:
            buf = active_benchmark_streams.get(run_id)
            if buf is None:
                buf = []
                active_benchmark_streams[run_id] = buf
            # Batch small chunks into existing buffer entry for the same kind to keep memory bounded
            if buf and buf[-1]["kind"] == kind and len(buf[-1]["text"]) < 2000:
                buf[-1]["text"] += text
            else:
                buf.append({"kind": kind, "text": text})
            if len(buf) > 20000:
                del buf[: len(buf) - 20000]

        try:
            update_run_status(run_id, "running", 10, "Running benchmarks...")

            results = run_benchmark(
                model_name=model_name,
                server_url=server_url,
                prompt_keys=prompt_list,
                context_size=context_size,
                max_tokens=max_tokens,
                temperature=temperature_value,
                top_p=top_p_value,
                num_runs=num_runs,
                enable_self_validation=use_self_validation,
                on_progress=lambda progress, step, tps, decoded: update_run_status(
                    run_id, "running", progress, step,
                    tokens_per_second=tps, decoded_tokens=decoded
                ),
                abort_flag=lambda: abort_flags.get(run_id, False),
                on_token=_on_token,
            )

            if results:
                # Save model to database
                model_id = create_model(model_name)

                # Save results with run_id
                for r in results:
                    r["model_id"] = model_id
                    r["run_id"] = run_id
                    result_id = create_result(r)
                    logger.info("Result saved (ID: %d, Score: %.2f, Run: %d)", result_id, r.get("final_score", 0), run_id)

                update_run_status(run_id, "finished", 100, "Benchmark completed.")
            else:
                update_run_status(run_id, "failed", 0, "No results",
                                  "Benchmark produced no usable results.")

        except Exception as e:
            logger.exception("Benchmark failed")
            update_run_status(run_id, "failed", 0, "Error", str(e))

    thread = threading.Thread(target=_run_benchmark, daemon=True)
    thread.start()
    active_benchmarks[run_id] = thread

    return {"run_id": run_id, "status": "running", "message": "Benchmark started."}


@app.get("/api/benchmark/status/{run_id}")
async def get_benchmark_status(run_id: int):
    """Return current status of a benchmark."""
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    data = dict(run)

    if data.get("status") == "running":
        live = get_live_llama_status(data["server_url"])
        decoded = live.get("decoded_tokens")
        tps = live.get("tokens_per_second")

        if decoded is not None:
            if live.get("decoded_source") == "metrics":
                baseline = live_decoded_baselines.setdefault(run_id, decoded)
                data["decoded_tokens"] = max(0, decoded - baseline)
            else:
                data["decoded_tokens"] = decoded
        if tps is not None and tps > 0:
            data["tokens_per_second"] = round(tps, 2)
        if live.get("source") in ("metrics", "slots"):
            data["metric_source"] = live["source"]
        elif data.get("tokens_per_second") is not None or data.get("decoded_tokens") is not None:
            data["metric_source"] = "stored"
        else:
            data["metric_source"] = "unavailable"

    return data


@app.get("/api/benchmark/active")
async def get_active_benchmark():
    """Return the newest currently active benchmark run, if any."""
    run = get_active_run()
    return {"run": run}


@app.post("/api/benchmark/abort/{run_id}")
async def abort_benchmark(run_id: int):
    """Abort a running benchmark."""
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    if run["status"] == "finished":
        return {"message": "Benchmark already completed."}

    # Set abort flag (checked by benchmark thread)
    abort_flags[run_id] = True
    logger.info("Abort requested for run %d", run_id)
    
    # Update status immediately
    update_run_status(run_id, "failed", 0, "Aborted", "Benchmark was aborted by user.")
    return {"message": "Benchmark is being aborted..."}


@app.get("/api/benchmark/logs/{run_id}")
async def get_benchmark_logs(run_id: int):
    """Return the in-memory captured log lines and live KI stream events for a benchmark run."""
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    lines = active_benchmark_logs.get(run_id, [])
    stream = active_benchmark_streams.get(run_id, [])
    # Stream events are returned as formatted lines for display, preserving kind via prefix
    stream_lines = []
    for ev in stream:
        kind = ev.get("kind", "content")
        text = ev.get("text", "")
        if kind == "thinking":
            stream_lines.append(f"[THINKING] {text}")
        elif kind == "status":
            stream_lines.append(f"[STATUS] {text}")
        else:
            stream_lines.append(text)
    return {
        "run_id": run_id,
        "status": run["status"],
        "lines": stream_lines,
        "total": len(stream_lines),
        "log_lines": list(lines),
    }


@app.get("/api/results")
async def api_results():
    """Return all results as JSON."""
    return get_all_results()


@app.get("/api/results/{result_id}")
async def api_result(result_id: int):
    """Return a single result."""
    result = get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found.")
    return result


@app.delete("/api/results/{result_id}")
async def api_delete_result(result_id: int):
    """Delete the full displayed result group."""
    if delete_result_run(result_id):
        return {"message": "Result group deleted."}
    raise HTTPException(status_code=404, detail="Result not found.")


@app.post("/api/results/{result_id}/quality-score")
async def api_update_quality(result_id: int, quality_score: float = Form(50)):
    """Update quality score."""
    if not (0 <= quality_score <= 100):
        raise HTTPException(status_code=400, detail="Score must be between 0 and 100.")
    if update_quality_score(result_id, quality_score):
        return {"message": "Quality score updated."}
    raise HTTPException(status_code=404, detail="Result not found.")


@app.get("/api/ranking")
async def api_ranking():
    """Return current ranking."""
    return get_all_results()


@app.get("/api/models")
async def api_models():
    """Return all saved models."""
    return get_all_models()


@app.get("/api/stats")
async def api_stats():
    """Return dashboard statistics."""
    return get_stats()
