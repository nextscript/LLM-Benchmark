"""
Scoring Module: Traceable multi-dimensional scoring inspired by SuperCalc Sicherheitsbenchmark.

Scoring dimensions:
  1. Performance Score   – tokens/s, latency (speed)
  2. Quality Score       – response structure, completeness, relevance, technical accuracy
  3. Format Score        – automatic format validation (JSON validity, code syntax, etc.)
  4. Stability Score     – error rate + variance across runs
  5. Context Score       – context size utilization
  6. Consistency Score   – similarity between Run 1 and Run 2 (self-validation)
"""

import json
import re
from typing import Dict, Any, List


# ──────────────────────────────────────────────
# Final score formula
# ──────────────────────────────────────────────

WEIGHTS = {
    "performance": 0.20,
    "quality": 0.30,
    "format": 0.15,
    "stability": 0.10,
    "context": 0.05,
    "consistency": 0.20,
}


def calculate_final_score(
    generation_tokens_per_second: float,
    prompt_tokens_per_second: float,
    quality_score: float = 50,
    stability_score: float = 100,
    context_score: float = 50,
    format_score: float = 50,
    consistency_score: float = 50,
    first_token_latency: float = 0,
) -> float:
    perf = _performance_score(generation_tokens_per_second, prompt_tokens_per_second, first_token_latency)
    score = (
        perf * WEIGHTS["performance"]
        + quality_score * WEIGHTS["quality"]
        + format_score * WEIGHTS["format"]
        + stability_score * WEIGHTS["stability"]
        + context_score * WEIGHTS["context"]
        + consistency_score * WEIGHTS["consistency"]
    )
    return round(score, 2)


def _performance_score(gen_tps: float, prompt_tps: float, first_token_latency: float) -> float:
    gen_part = min(gen_tps / 50.0, 1.0) * 100
    prompt_part = min(prompt_tps / 500.0, 1.0) * 100
    latency_penalty = 0
    if first_token_latency > 0:
        latency_penalty = min(first_token_latency / 10000.0, 1.0) * 30
    return max(0, gen_part * 0.5 + prompt_part * 0.3 + (100 - latency_penalty) * 0.2)


# ──────────────────────────────────────────────
# Quality Score – automatic response evaluation
# ──────────────────────────────────────────────

def evaluate_response_quality(content: str, prompt_name: str) -> Dict[str, float]:
    scores = {
        "structure": _score_structure(content),
        "completeness": _score_completeness(content),
        "relevance": _score_relevance(content, prompt_name),
        "technical_accuracy": _score_technical(content, prompt_name),
    }
    weights = {"structure": 0.20, "completeness": 0.25, "relevance": 0.30, "technical_accuracy": 0.25}
    total = sum(scores[k] * weights[k] for k in scores)
    scores["total"] = round(total, 2)
    return scores


def _score_structure(content: str) -> float:
    if not content or len(content.strip()) < 10:
        return 0.0
    score = 50.0
    if "\n" in content:
        score += 10
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if len(paragraphs) >= 2:
        score += 10
    if re.search(r"```", content):
        score += 10
    if re.search(r"[-*]\s", content):
        score += 5
    if re.search(r"\d+\.\s", content):
        score += 5
    lines = content.strip().split("\n")
    if len(lines) >= 5:
        score += 5
    if len(lines) >= 15:
        score += 5
    return min(score, 100.0)


def _score_completeness(content: str) -> float:
    if not content:
        return 0.0
    word_count = len(content.split())
    if word_count < 10:
        return 10.0
    if word_count < 30:
        return 30.0
    if word_count < 80:
        return 50.0
    if word_count < 150:
        return 70.0
    if word_count < 300:
        return 85.0
    return 100.0


def _score_relevance(content: str, prompt_name: str) -> float:
    if not content:
        return 0.0
    lower = content.lower()
    keywords = _get_expected_keywords(prompt_name)
    if not keywords:
        return 60.0
    found = sum(1 for kw in keywords if kw in lower)
    ratio = found / len(keywords)
    return round(ratio * 100, 2)


def _get_expected_keywords(prompt_name: str) -> List[str]:
    keyword_map = {
        "Coding Test": ["def", "function", "read", "file", "error", "return", "dict", "log", "line", "open"],
        "Reasoning Test": ["worker", "parallel", "request", "second", "120", "80", "queue", "concurrent", "thread", "latency"],
        "Long Context Test": ["summary", "error", "risk", "improvement", "project", "architecture", "benchmark", "database", "feature", "security"],
        "German Text Test": ["server", "modell", "token", "latenz", "kontext", "gpu", "cpu", "speicher", "anfrage", "antwort"],
        "JSON Test": ["model", "context", "thread", "gpu", "temperature", "path", "layer", "n_ctx", "n_gpu_layers"],
    }
    return keyword_map.get(prompt_name, [])


def _score_technical(content: str, prompt_name: str) -> float:
    if not content:
        return 0.0
    score = 40.0
    if "Coding Test" in prompt_name:
        if re.search(r"def\s+\w+\s*\(", content):
            score += 20
        if "try" in content and "except" in content:
            score += 15
        if "import" in content:
            score += 10
        if "with open" in content or "open(" in content:
            score += 15
    elif "Reasoning Test" in prompt_name:
        if re.search(r"\d+", content):
            score += 20
        if any(w in content.lower() for w in ["because", "therefore", "thus", "since", "denn", "weil", "daher"]):
            score += 20
        if any(w in content.lower() for w in ["little", "law", "utilization", "queue"]):
            score += 20
    elif "JSON Test" in prompt_name:
        json_score = validate_json_format(content)
        score = json_score
    elif "German Text Test" in prompt_name:
        german_words = ["der", "die", "das", "und", "ist", "ein", "eine", "mit", "auf", "für"]
        found = sum(1 for w in german_words if w in content.lower())
        score += min(found * 6, 40)
        if len(content) > 200:
            score += 20
    elif "Long Context Test" in prompt_name:
        if any(w in content.lower() for w in ["error", "risk", "improvement", "fehler", "risiko", "verbesserung"]):
            score += 20
        if re.search(r"[-*]\s", content) or re.search(r"\d+\.\s", content):
            score += 20
        if len(content) > 300:
            score += 20
    return min(score, 100.0)


# ──────────────────────────────────────────────
# Format Score – automatic format validation
# ──────────────────────────────────────────────

def validate_format(content: str, prompt_name: str) -> Dict[str, Any]:
    result = {"format_score": 50.0, "checks": [], "passed": 0, "total": 0}

    if "JSON Test" in prompt_name:
        result["total"] = 3
        json_valid = validate_json_format(content)
        result["checks"].append({"name": "valid_json", "passed": json_valid >= 70, "detail": f"JSON score: {json_valid}"})
        has_braces = "{" in content and "}" in content
        result["checks"].append({"name": "has_json_structure", "passed": has_braces, "detail": ""})
        has_keys = bool(re.search(r'"[^"]+"\s*:', content))
        result["checks"].append({"name": "has_key_value_pairs", "passed": has_keys, "detail": ""})
        result["passed"] = sum(1 for c in result["checks"] if c["passed"])
        result["format_score"] = round((result["passed"] / result["total"]) * 100, 2) if result["total"] > 0 else 50.0

    elif "Coding Test" in prompt_name:
        result["total"] = 4
        has_def = bool(re.search(r"def\s+\w+\s*\(", content))
        result["checks"].append({"name": "has_function_definition", "passed": has_def, "detail": ""})
        has_return = "return" in content
        result["checks"].append({"name": "has_return_statement", "passed": has_return, "detail": ""})
        has_docstring = bool(re.search(r'("""|\'\'\')', content))
        result["checks"].append({"name": "has_docstring", "passed": has_docstring, "detail": ""})
        has_error_handling = "try" in content and "except" in content
        result["checks"].append({"name": "has_error_handling", "passed": has_error_handling, "detail": ""})
        result["passed"] = sum(1 for c in result["checks"] if c["passed"])
        result["format_score"] = round((result["passed"] / result["total"]) * 100, 2) if result["total"] > 0 else 50.0

    elif "Reasoning Test" in prompt_name:
        result["total"] = 3
        has_calculation = bool(re.search(r"\d+\s*[*+\-/]\s*\d+", content))
        result["checks"].append({"name": "has_calculation", "passed": has_calculation, "detail": ""})
        has_result = bool(re.search(r"=\s*\d+|:\s*\d+|is\s+\d+", content))
        result["checks"].append({"name": "has_numerical_result", "passed": has_result, "detail": ""})
        has_explanation = len(content.split()) > 30
        result["checks"].append({"name": "has_explanation", "passed": has_explanation, "detail": ""})
        result["passed"] = sum(1 for c in result["checks"] if c["passed"])
        result["format_score"] = round((result["passed"] / result["total"]) * 100, 2) if result["total"] > 0 else 50.0

    else:
        result["total"] = 2
        has_content = len(content.strip()) > 50
        result["checks"].append({"name": "has_substantial_content", "passed": has_content, "detail": ""})
        has_structure = "\n" in content or len(content.split()) > 30
        result["checks"].append({"name": "has_structure", "passed": has_structure, "detail": ""})
        result["passed"] = sum(1 for c in result["checks"] if c["passed"])
        result["format_score"] = round((result["passed"] / result["total"]) * 100, 2) if result["total"] > 0 else 50.0

    return result


def validate_json_format(content: str) -> float:
    json_match = re.search(r'\{[\s\S]*\}', content)
    if not json_match:
        return 0.0
    json_str = json_match.group()
    try:
        parsed = json.loads(json_str)
        if isinstance(parsed, dict) and len(parsed) >= 3:
            return 100.0
        elif isinstance(parsed, dict):
            return 80.0
        return 60.0
    except json.JSONDecodeError:
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            json.loads(json_str)
            return 50.0
        except json.JSONDecodeError:
            return 20.0


# ──────────────────────────────────────────────
# Stability Score
# ──────────────────────────────────────────────

def calculate_stability_score(error_count: int, total_runs: int) -> float:
    """Calculate stability based on error count (as per README).
    
    Based on README:
    - No errors (0/total) → 100
    - Minor errors (1-4/total if total >= 5) → 75
    - Timeout (5-9/total if total >= 10) → 50
    - Multiple errors (10-14/total if total >= 15) → 25
    - Completely failed (15+) → 0
    """
    if total_runs == 0:
        return 0.0
    
    # Calculate error rate
    error_rate = error_count / total_runs
    
    # Use error count thresholds as per README
    if error_count == 0:
        return 100.0  # No errors
    elif error_rate <= 0.20:  # Minor errors (fewer than 20%)
        return 75.0
    elif error_rate <= 0.40:  # Timeout (20-40% errors)
        return 50.0
    elif error_rate <= 0.60:  # Multiple errors (40-60% errors)
        return 25.0
    else:
        return 0.0  # Completely failed (60%+ errors)


def calculate_stability_from_runs(results: List[Dict[str, Any]], error_count: int = 0, total_runs: int = 0) -> float:
    """Calculate stability based on error count (as per README)."""
    if total_runs == 0:
        return 100.0 if results else 0.0
    
    # Use error count as per README specification
    return calculate_stability_score(error_count, total_runs)


# ──────────────────────────────────────────────
# Consistency Score (Run 1 vs Run 2)
# ──────────────────────────────────────────────

def calculate_consistency_score(run1_content: str, run2_content: str) -> Dict[str, float]:
    if not run1_content or not run2_content:
        return {"total": 50.0, "length_similarity": 50.0, "keyword_overlap": 50.0, "structure_similarity": 50.0}

    len1, len2 = len(run1_content), len(run2_content)
    max_len = max(len1, len2, 1)
    length_sim = (1.0 - abs(len1 - len2) / max_len) * 100

    words1 = set(run1_content.lower().split())
    words2 = set(run2_content.lower().split())
    if words1 and words2:
        intersection = words1 & words2
        union = words1 | words2
        keyword_overlap = (len(intersection) / len(union)) * 100
    else:
        keyword_overlap = 0.0

    struct1 = _extract_structure_features(run1_content)
    struct2 = _extract_structure_features(run2_content)
    struct_sim = _compare_structure(struct1, struct2)

    total = length_sim * 0.25 + keyword_overlap * 0.50 + struct_sim * 0.25

    return {
        "total": round(total, 2),
        "length_similarity": round(length_sim, 2),
        "keyword_overlap": round(keyword_overlap, 2),
        "structure_similarity": round(struct_sim, 2),
    }


def _extract_structure_features(content: str) -> Dict[str, int]:
    return {
        "paragraphs": len([p for p in content.split("\n\n") if p.strip()]),
        "code_blocks": len(re.findall(r"```", content)),
        "bullet_points": len(re.findall(r"[-*]\s", content)),
        "numbered_items": len(re.findall(r"\d+\.\s", content)),
        "lines": len(content.strip().split("\n")),
    }


def _compare_structure(f1: Dict[str, int], f2: Dict[str, int]) -> float:
    scores = []
    for key in f1:
        v1, v2 = f1[key], f2[key]
        max_v = max(v1, v2, 1)
        sim = (1.0 - abs(v1 - v2) / max_v) * 100
        scores.append(sim)
    return sum(scores) / len(scores) if scores else 50.0


# ──────────────────────────────────────────────
# Context Score
# ──────────────────────────────────────────────

def calculate_context_score(context_size: int) -> float:
    return min(context_size / 1000.0, 100.0)


# ──────────────────────────────────────────────
# Full scoring pipeline for a single result
# ──────────────────────────────────────────────

def score_result(result: Dict[str, Any], run1_content: str = "", run2_content: str = "") -> Dict[str, Any]:
    prompt_name = result.get("prompt_name", "")
    content = result.get("content", "")

    quality = evaluate_response_quality(content, prompt_name)
    fmt = validate_format(content, prompt_name)
    consistency = calculate_consistency_score(run1_content, run2_content) if run2_content else {"total": 50.0}
    context = calculate_context_score(result.get("context_size", 4096))
    stability = result.get("stability_score", 100.0)

    final = calculate_final_score(
        generation_tokens_per_second=result.get("generation_tokens_per_second", 0),
        prompt_tokens_per_second=result.get("prompt_tokens_per_second", 0),
        quality_score=quality["total"],
        stability_score=stability,
        context_score=context,
        format_score=fmt["format_score"],
        consistency_score=consistency["total"],
        first_token_latency=result.get("first_token_latency", 0) or 0,
    )

    return {
        "quality_score": quality["total"],
        "quality_details": quality,
        "format_score": fmt["format_score"],
        "format_checks": fmt["checks"],
        "format_passed": fmt["passed"],
        "format_total": fmt["total"],
        "consistency_score": consistency["total"],
        "consistency_details": consistency,
        "context_score": context,
        "stability_score": stability,
        "final_score": final,
    }


# ──────────────────────────────────────────────
# Language Score (multi-language coding tests)
# ──────────────────────────────────────────────

LANGUAGE_SYNTAX_MARKERS = {
    "python": [r'\bdef\s+', r'try:', r'except\b', r'with\s+open|pathlib|os\.', r'return\b'],
    "javascript": [r'async\s+function|const\s+.*=>|function\s+', r'fetch\s*\(|addEventListener|document\.', r'try\s*{', r'return\b'],
    "typescript": [r'interface\s+|type\s+', r'<T>|generic', r':\s*Promise|async\s+', r'Result|ApiResponse', r'no\s+any|any'],
    "java": [r'public\s+class', r'public\s+static\s+void\s+main', r'Optional<|ExecutorService|try\s*\(', r'Map<|List<'],
    "csharp": [r'using\s+System', r'class\s+', r'async\s+|Task<', r'LINQ|IEnumerable|interface', r'public\s+'],
    "cpp": [r'#include', r'std::', r'class\s+|struct\s+', r'int\s+main\s*\(', r'std::vector|std::unordered_map|std::unique_ptr'],
    "c": [r'#include', r'int\s+main\s*\(', r'malloc|calloc|free', r'struct\s+', r'fopen|strtol'],
    "go": [r'package\s+main', r'func\s+main\s*\(', r'go\s+', r'chan\b|<-', r'sync\.WaitGroup|net/http'],
    "rust": [r'fn\s+', r'Result<', r'HashMap', r'trait\s+|enum\s+', r'#\[test\]'],
    "php": [r'<\?php', r'declare\(strict_types=1\)', r'PDO|filter_var|password_hash', r'class\s+|function\s+', r'prepare\s*\('],
    "ruby": [r'def\s+', r'class\s+', r'ARGV|File\.', r'rescue\b', r'sort_by|group_by'],
    "kotlin": [r'data\s+class', r'fun\s+', r'suspend\s+|coroutineScope|async', r'\?:', r'List<'],
    "swift": [r'struct\s+|class\s+', r'protocol\s+', r'async\s+|await', r'Codable', r'func\s+'],
    "dart": [r'class\s+', r'Future<|async', r'Widget|StatelessWidget', r'List<', r'void\s+main|Widget\s+build'],
    "sql": [r'SELECT\s+', r'JOIN|GROUP\s+BY', r'WHERE\s+', r'ORDER\s+BY', r'COUNT\(|SUM\('],
    "bash": [r'#!/usr/bin/env\s+bash|#!/bin/bash', r'set\s+-euo\s+pipefail', r'find\s+|tar\s+|grep\s+', r'\$\{.*\}|\"\$', r'exit\s+'],
    "powershell": [r'param\s*\(', r'Get-CimInstance|Get-Service|Get-ChildItem', r'try\s*{', r'ConvertTo-Json|Restart-Service|Remove-Item', r'Write-Host|Write-Output'],
}


def _score_language_syntax(content: str, language: str) -> float:
    """Score how well the code uses idiomatic syntax for the given language."""
    if not language or language not in LANGUAGE_SYNTAX_MARKERS:
        return 50.0
    if not content.strip():
        return 0.0
    markers = LANGUAGE_SYNTAX_MARKERS[language]
    found = 0
    for marker in markers:
        if re.search(marker, content, re.IGNORECASE):
            found += 1
    return min(100.0, (found / len(markers)) * 100.0)


def score_required_checks(content: str, checks: list) -> float:
    """Check how many required keywords are present in the output."""
    if not checks:
        return 50.0
    content_lower = content.lower()
    hits = 0
    for check in checks:
        normalized = check.lower().replace("_", " ")
        compact = check.lower().replace("_", "")
        check_lower = check.lower()
        if normalized in content_lower or compact in content_lower or check_lower in content_lower:
            hits += 1
    return min(100.0, (hits / len(checks)) * 100.0)


def calculate_language_score(
    content: str,
    language: str | None,
    checks: list[str] | None = None,
    quality_score: float = 50,
    format_score: float = 50,
) -> dict:
    """Calculate a language-specific coding score (0–100).

    Returns:
        {"score": 0-100, "rating": "good"|"medium"|"bad",
         "label": "Can do well"|"Can do medium"|"Can do poorly"}
    """
    if checks is None:
        checks = []

    language_score = 50.0
    if language:
        language_score = _score_language_syntax(content, language)

    checks_score = score_required_checks(content, checks)

    score = (
        quality_score * 0.45
        + format_score * 0.25
        + language_score * 0.20
        + checks_score * 0.10
    )
    score = round(min(100, max(0, score)), 1)

    if score >= 75:
        rating = "good"
        label = "Can do well"
    elif score >= 45:
        rating = "medium"
        label = "Can do medium"
    else:
        rating = "bad"
        label = "Can do poorly"

    return {
        "score": score,
        "rating": rating,
        "label": label,
    }


# ──────────────────────────────────────────────
# Engine Score (game engine / graphics tests)
# ──────────────────────────────────────────────

ENGINE_SYNTAX_MARKERS = {
    "vulkan": [
        r'vkCreate|Vk[A-Z]|VK_',
        r'swapchain|VkSwapchainKHR',
        r'command.?buffer|vkCmd',
        r'semaphore|fence',
        r'pipeline|VkPipeline',
        r'render.?pass|VkRenderPass',
        r'descriptor',
        r'validation.?layer',
    ],
    "glsl": [
        r'#version\s+\d+',
        r'layout\s*\(',
        r'uniform\s+|in\s+|out\s+',
        r'vec[234]|mat[234]',
        r'texture\(|sampler',
        r'void\s+main\s*\(',
        r'gl_Position|gl_FragCoord',
        r'compute|work_group|shared',
    ],
    "hlsl": [
        r'cbuffer|ConstantBuffer',
        r'Texture2D|SamplerState',
        r'SV_POSITION|SV_Target',
        r'struct\s+\w+VS|\w+PS',
        r'register\s*\(',
        r'float[234]|half[234]',
        r'mul\s*\(|dot\s*\(|cross\s*\(',
        r'void\s+VS|void\s+PS|float4\s+PS',
    ],
    "opengl": [
        r'gl[A-Z]|GL_',
        r'glCreateShader|glCompileShader',
        r'glGenFramebuffers|glBindFramebuffer',
        r'VAO|VBO|EBO|glVertexAttrib',
        r'glDrawArrays|glDrawElements',
        r'shader|fragment|vertex',
        r'glUniform|glGetUniformLocation',
        r'glEnable|glDisable',
    ],
    "directx12": [
        r'D3D12|ID3D12',
        r'ResourceBarrier',
        r'command.?list|ID3D12GraphicsCommandList',
        r'descriptor.?heap',
        r'root.?signature',
        r'RTV|DSV|SRV|UAV',
        r'ComPtr|D3D12_RESOURCE_STATE',
        r'CreateDevice|D3D12CreateDevice',
    ],
    "webgpu": [
        r'navigator\.gpu|requestAdapter',
        r'requestDevice|GPUDevice',
        r'GPURenderPipeline|createRenderPipeline',
        r'WGSL|@vertex|@fragment|@compute',
        r'GPUCommandEncoder|createCommandEncoder',
        r'queue\.submit',
        r'canvas.?context|getContext',
        r'GPUBuffer|createBuffer',
    ],
    "unity": [
        r'MonoBehaviour|ScriptableObject',
        r'ScriptableRendererFeature|ScriptableRenderPass',
        r'NativeArray|IJobParallelFor|Burst',
        r'Addressables|AsyncOperationHandle',
        r'\[SerializeField\]|\[Header\]',
        r'OnEnable|OnDisable|Update|Start',
        r'GetComponent|AddComponent',
        r'Blit|RenderPassEvent',
    ],
    "unreal": [
        r'AActor|UObject|UPROPERTY|UFUNCTION',
        r'GetLifetimeReplicatedProps',
        r'Server|Client|NetMulticast',
        r'GameplayAbility|GameplayEffect',
        r'HasAuthority|Role|RemoteRole',
        r'OnRep_|ReplicatedUsing',
        r'Blueprint|BlueprintImplementableEvent',
        r'RDG|FRDGBuilder|AddRDGPass',
    ],
    "godot": [
        r'extends\s+|class_name',
        r'signal\s+\w+',
        r'@export|@onready',
        r'func\s+_ready|func\s+_process',
        r'shader_type|render_mode',
        r'RenderingDevice|ComputeShader',
        r'get_node|get_tree',
        r'GDScript|Node|Scene',
    ],
    "render_pipeline": [
        r'G.?buffer|depth.?pre.?pass',
        r'forward.?plus|deferred|tiled',
        r'light.?culling|cluster',
        r'render.?graph|pass.?order',
        r'tone.?mapping|bloom|HDR',
        r'transient.?resource|barrier',
        r'topological.?sort|dependency',
        r'sRGB|linear.?color',
    ],
    "shader_debugging": [
        r'RenderDoc|render.?doc',
        r'shader.?compil|link.?error',
        r'vertex.?layout|input.?layout',
        r'depth.?test|culling|winding',
        r'TBN|tangent.?space|normal.?matrix',
        r'handedness|bitangent',
        r'camera.?matrix|projection|view',
        r'uniform|descriptor|binding',
    ],
    "gpu_performance": [
        r'CPU.?frame.?time|GPU.?frame.?time',
        r'overdraw|shader.?complexity',
        r'draw.?call|batch|instancing',
        r'frustum.?culling|occlusion',
        r'LOD|level.?of.?detail',
        r'VRAM|texture.?compression|mipmap',
        r'streaming|memory.?budget',
        r'profiler|RenderDoc|GPU.?trace',
    ],
    "physics": [
        r'AABB|bounding.?box',
        r'overlap|collision|MTV',
        r'tunneling|CCD|continuous',
        r'quadtree|octree|BVH|grid',
        r'broadphase|narrowphase',
        r'rigid.?body|dynamic|static',
        r'spatial.?partition',
        r'resolve|penetration|separation',
    ],
    "multiplayer": [
        r'client.?prediction|server.?reconciliation',
        r'input.?sequence|tick.?rate',
        r'snapshot|interpolation',
        r'packet.?loss|jitter|latency',
        r'authoritative|desync',
        r'smooth|correction|replay',
        r'buffer|delay|lag.?compensation',
        r'RPC|replication|network',
    ],
    "asset_pipeline": [
        r'glTF|gltf',
        r'mesh|material|texture|skeleton|animation',
        r'tangent|normal.?map',
        r'binary.?cache|hot.?reload',
        r'texture.?compression|mipmap',
        r'sRGB|linear',
        r'streaming|memory.?budget',
        r'import|export|convert',
    ],
    "editor_tools": [
        r'editor.?tool|custom.?inspector',
        r'missing.?material|missing.?collision',
        r'broken.?reference|oversized',
        r'severity|warning|error',
        r'JSON.?report|export',
        r'FPS|frame.?time|draw.?call',
        r'debug.?overlay|toggle',
        r'memory|triangles|overhead',
    ],
    "gameplay_systems": [
        r'inventory|stackable|metadata',
        r'save.?load|versioning|migration',
        r'serializ|deserializ',
        r'quest.?state|world.?state',
        r'atomic.?write|corrupt',
        r'split.?stack|edge.?case',
        r'schema|data.?structure',
        r'add|remove|update|find',
    ],
    "2d": [
        r'tilemap|tile.?map|chunk',
        r'batch|sprite|atlas',
        r'camera.?culling|viewport',
        r'pixel.?perfect|integer.?scaling',
        r'subpixel|jitter',
        r'render.?texture|UI.?scaling',
        r'animated.?tile|collision',
        r'dirty.?chunk|update',
    ],
    "3d": [
        r'skeleton|bone|inverse.?bind',
        r'keyframe|interpolation|blending',
        r'GPU.?skinning|CPU.?skinning',
        r'LOD|frustum.?culling|occlusion',
        r'streaming|chunk|memory.?budget',
        r'popping|fade|transition',
        r'animation.?state|blend.?tree',
        r'matrix|transform|hierarchy',
    ],
}


def _score_engine_syntax(content: str, engine_skill: str) -> float:
    if not engine_skill or engine_skill not in ENGINE_SYNTAX_MARKERS:
        return 50.0
    if not content.strip():
        return 0.0
    markers = ENGINE_SYNTAX_MARKERS[engine_skill]
    found = 0
    for marker in markers:
        if re.search(marker, content, re.IGNORECASE):
            found += 1
    return min(100.0, (found / len(markers)) * 100.0)


def calculate_engine_score(
    content: str,
    engine_skill: str | None,
    checks: list[str] | None = None,
    quality_score: float = 50,
    format_score: float = 50,
) -> dict:
    """Calculate an engine-specific score (0–100).

    Returns:
        {"score": 0-100, "rating": "good"|"medium"|"bad",
         "label": "Can do well"|"Can do medium"|"Can do poorly"}
    """
    if checks is None:
        checks = []

    engine_syntax_score = 50.0
    if engine_skill:
        engine_syntax_score = _score_engine_syntax(content, engine_skill)

    checks_score = score_required_checks(content, checks)

    score = (
        quality_score * 0.45
        + format_score * 0.25
        + engine_syntax_score * 0.20
        + checks_score * 0.10
    )
    score = round(min(100, max(0, score)), 1)

    if score >= 75:
        rating = "good"
        label = "Can do well"
    elif score >= 45:
        rating = "medium"
        label = "Can do medium"
    else:
        rating = "bad"
        label = "Can do poorly"

    return {
        "score": score,
        "rating": rating,
        "label": label,
    }


# Songwriting Score

SONGWRITING_CRITERIA = {
    "hook": "Hook",
    "rhyme": "Rhyme",
    "meter": "Meter",
    "emotion": "Emotion",
    "structure": "Structure",
    "originality": "Originality",
}

CLICHE_PHRASES = [
    "broken heart", "tears fall", "in the rain", "darkness inside", "lost without you",
    "heart on fire", "can't breathe without you", "schmerz in meinem herz",
]


def _rating_for_score(score: float) -> dict:
    if score >= 75:
        return {"rating": "good", "label": "Strong"}
    if score >= 45:
        return {"rating": "medium", "label": "Moderate"}
    return {"rating": "bad", "label": "Weak"}


def _lyric_lines(content: str) -> List[str]:
    lines = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("```"):
            continue
        if re.match(r"^\s*[-*]\s+", line):
            line = re.sub(r"^\s*[-*]\s+", "", line).strip()
        lines.append(line)
    return lines


def _contains_any(content: str, terms: List[str]) -> bool:
    lower = content.lower()
    return any(term.lower() in lower for term in terms)


def _line_length_score(lines: List[str]) -> float:
    lyric_lines = [line for line in lines if not re.match(r"^\[[^\]]+\]$", line)]
    if not lyric_lines:
        return 0.0
    word_counts = [len(re.findall(r"\w+", line, re.UNICODE)) for line in lyric_lines]
    short_ratio = sum(1 for count in word_counts if 2 <= count <= 9) / len(word_counts)
    avg = sum(word_counts) / len(word_counts)
    consistency = max(0.0, 100.0 - (max(word_counts) - min(word_counts)) * 8) if len(word_counts) > 1 else 60.0
    return round(short_ratio * 65 + min(avg / 8, 1) * 15 + consistency * 0.20, 1)


def _rhyme_score(lines: List[str], checks: List[str]) -> float:
    lyric_lines = [re.sub(r"[^\w\s]", "", line.lower()).strip() for line in lines if not line.startswith("[")]
    endings = []
    for line in lyric_lines:
        words = re.findall(r"\w+", line, re.UNICODE)
        if words:
            endings.append(words[-1][-3:])
    if len(endings) < 2:
        return 45.0 if "rhyme" in checks else 35.0
    pairs = sum(1 for a, b in zip(endings, endings[1:]) if a == b)
    repeated_endings = len(endings) - len(set(endings))
    score = 35 + pairs * 18 + repeated_endings * 10
    if "rhyme" in checks or "end_rhyme" in checks:
        score += 10
    return round(min(100.0, score), 1)


def _structure_score(content: str, lines: List[str], checks: List[str]) -> float:
    tags = re.findall(r"\[[^\]]+\]", content)
    expected_sections = ["verse", "chorus", "hook", "bridge", "pre-chorus", "pre-hook", "outro", "drop"]
    section_hits = sum(1 for section in expected_sections if section in content.lower())
    score = 35 + min(len(tags), 8) * 7 + min(section_hits, 6) * 5
    if "full_song" in checks or "structure" in checks or "section_tags" in checks:
        score += 10
    if len(lines) >= 4:
        score += 10
    return round(min(100.0, score), 1)


def _emotion_score(content: str, checks: List[str]) -> float:
    emotion_words = [
        "love", "miss", "regret", "alive", "lonely", "chance", "heart", "feel",
        "liebe", "vermiss", "bereu", "sehnsucht", "καρδι", "αγαπ", "λείπ",
        "amor", "duele", "nostalgic", "euphoric",
    ]
    hits = sum(1 for word in emotion_words if word in content.lower())
    score = 40 + min(hits, 8) * 7
    if "emotion" in checks or "regret" in checks or "euphoria" in checks:
        score += 10
    return round(min(100.0, score), 1)


def _hook_score(content: str, lines: List[str], checks: List[str]) -> float:
    lower_lines = [line.lower().strip(" .,!?") for line in lines if line and not line.startswith("[")]
    repeated = len(lower_lines) - len(set(lower_lines))
    short_memorable = sum(1 for line in lower_lines if 2 <= len(line.split()) <= 8)
    score = 35 + min(repeated, 3) * 15 + min(short_memorable, 6) * 6
    if _contains_any(content, ["chorus", "hook", "refrain", "nakarat"]):
        score += 10
    if "hook" in checks or "chorus" in checks:
        score += 10
    return round(min(100.0, score), 1)


def _originality_score(content: str, checks: List[str]) -> float:
    lower = content.lower()
    cliche_penalty = sum(1 for phrase in CLICHE_PHRASES if phrase in lower) * 10
    words = re.findall(r"\w+", lower, re.UNICODE)
    unique_ratio = len(set(words)) / len(words) if words else 0
    score = 45 + min(unique_ratio, 0.75) * 60 - cliche_penalty
    if "originality" in checks or "no_cliche" in checks or "fresh_wording" in checks:
        score += 8
    return round(min(100.0, max(0.0, score)), 1)


def calculate_songwriting_scores(
    content: str,
    checks: list[str] | None = None,
    quality_score: float = 50,
    format_score: float = 50,
) -> dict:
    """Calculate separate songwriting criteria and an overall score."""
    if checks is None:
        checks = []
    normalized_checks = [c.lower() for c in checks]
    lines = _lyric_lines(content)

    criteria_scores = {
        "hook": _hook_score(content, lines, normalized_checks),
        "rhyme": _rhyme_score(lines, normalized_checks),
        "meter": _line_length_score(lines),
        "emotion": _emotion_score(content, normalized_checks),
        "structure": _structure_score(content, lines, normalized_checks),
        "originality": _originality_score(content, normalized_checks),
    }

    checks_score = score_required_checks(content, checks)
    weighted = (
        criteria_scores["hook"] * 0.18
        + criteria_scores["rhyme"] * 0.12
        + criteria_scores["meter"] * 0.15
        + criteria_scores["emotion"] * 0.15
        + criteria_scores["structure"] * 0.18
        + criteria_scores["originality"] * 0.17
        + checks_score * 0.05
    )
    score = round(min(100, max(0, weighted * 0.80 + quality_score * 0.12 + format_score * 0.08)), 1)
    rating = _rating_for_score(score)

    result = {
        "score": score,
        "rating": rating["rating"],
        "label": rating["label"],
    }
    for key, value in criteria_scores.items():
        detail_rating = _rating_for_score(value)
        result[f"{key}_score"] = value
        result[f"{key}_rating"] = detail_rating["rating"]
        result[f"{key}_rating_label"] = detail_rating["label"]
    return result
