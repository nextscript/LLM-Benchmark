"""
Benchmark Module: Multi-pass benchmark execution with traceable scoring.

Inspired by SuperCalc Sicherheitsbenchmark:
  - Run 1: Blind prompt (no hints)
  - Run 2: Self-validation (model reviews its own Run-1 answer)
  - Consistency measurement between runs
  - Per-prompt quality, format, and consistency scoring
"""

import ast
import logging
import os
import re
from typing import Optional, Dict, Any, List, Callable

from llama_client import check_health, send_completion, send_chat_completion, get_system_metrics
from scoring import (
    calculate_final_score,
    calculate_stability_from_runs,
    calculate_context_score,
    calculate_language_score,
    calculate_engine_score,
    calculate_songwriting_scores,
    evaluate_response_quality,
    validate_format,
    calculate_consistency_score,
)

logger = logging.getLogger(__name__)

PROMPTS = {
    "coding": {
        "name": "Coding Test",
        "text": "Write a clean Python function that reads a large log file line by line, detects errors, and returns a summary as a dictionary.",
        "self_validation_hint": "Review your previous answer. Does it include proper error handling with try/except? Does it have a docstring? Is the function signature clear? Improve if needed.",
    },
    "reasoning": {
        "name": "Reasoning Test",
        "text": "A server processes 120 requests per second. Each request takes an average of 80 ms. How many parallel workers are needed at minimum? Explain briefly.",
        "self_validation_hint": "Review your calculation. Did you use Little's Law or similar reasoning? Is your numerical answer correct? Verify and improve if needed.",
    },
    "long_context": {
        "name": "Long Context Test",
        "text": (
            "Summarize the following long project text in a structured way and identify possible errors, risks, and improvements.\n\n"
            "=== PROJECT DOCUMENTATION ===\n\n"
            "Project: Llama Model Benchmark WebGUI\n"
            "Version: 1.0.0\n"
            "Status: In development\n\n"
            "Description:\n"
            "This project is a local benchmark web GUI that allows testing, comparing, and automatically ranking various llama.cpp / llama-server models. "
            "The application benchmarks models, stores all measurements, and creates a ranking to help determine the best model for your own hardware and use case.\n\n"
            "Technical Stack:\n"
            "- Backend: Python with FastAPI\n"
            "- Frontend: Bootstrap 5 with dark theme\n"
            "- Database: SQLite for persistent storage\n"
            "- Communication: OpenAI-compatible API endpoints with llama-server\n"
            "- Language: English as primary UI language\n\n"
            "Architecture:\n"
            "The application follows a modular structure. The backend consists of multiple files: app.py for FastAPI routes, database.py for SQLite operations, benchmark.py for benchmark logic, "
            "llama_client.py for server communication, and scoring.py for score calculation. The frontend uses Jinja2 templates with Bootstrap 5 and JavaScript for live status updates.\n\n"
            "Benchmark Process:\n"
            "1. User opens web GUI and enters model name and server URL\n"
            "2. User selects test prompts from a predefined list\n"
            "3. Backend checks server connection via /health endpoint\n"
            "4. Frontend shows animation and progress bar\n"
            "5. Backend sends prompts to llama-server and measures all times and tokens\n"
            "6. Backend calculates score and saves result to SQLite\n"
            "7. Frontend plays sound and shows modal after completion\n\n"
            "Ranking System:\n"
            "The score is calculated from multiple metrics: Generation Tokens/s (40%), Prompt Tokens/s (20%), Quality Score (25%), Stability Score (10%), Context Score (5%). "
            "The ranking sorts by highest total score, highest Generation Tokens/s, lowest First Token Latency, highest stability, and lowest error rate.\n\n"
            "Known Issues:\n"
            "- VRAM detection only works with NVIDIA GPUs and nvidia-smi\n"
            "- Quality Score is currently set to 50 as default value\n"
            "- RAM usage is measured via psutil but not always accurate\n"
            "- llama-server can become slow with very large context sizes\n"
            "- First Token Latency is not returned by all endpoints\n"
            "- Timeout on long prompts can lead to failed benchmarks\n\n"
            "Planned Features:\n"
            "- Manual quality rating via API endpoint\n"
            "- Export results as CSV or JSON\n"
            "- Comparison view for multiple models\n"
            "- Automatic server start/stop management\n"
            "- GPU temperature and power usage monitoring\n"
            "- Configurable prompt collections\n\n"
            "Security Notes:\n"
            "- The application runs locally and is not intended for production use on the internet\n"
            "- No authentication implemented\n"
            "- Server URL is entered by user, no validation\n"
            "- SQLite database is stored unencrypted on disk\n\n"
            "=== END OF PROJECT DOCUMENTATION ==="
        ),
        "self_validation_hint": "Review your summary. Did you identify at least 3 risks? Did you mention improvements? Is the structure clear with bullet points or numbered lists? Improve if needed.",
    },
    "german_text": {
        "name": "German Text Test",
        "text": "Write a clear technical explanation in German about why a local LLM server might respond slowly.",
        "self_validation_hint": "Review your German text. Is it written entirely in German? Does it cover at least 3 reasons (e.g., context size, GPU memory, token count)? Improve if needed.",
    },
    "json_test": {
        "name": "JSON Test",
        "text": "Create a valid JSON configuration for a local Llama server with model path, context size, threads, GPU layers, and temperature.",
        "self_validation_hint": "Review your JSON. Is it valid JSON that can be parsed? Does it contain all required keys (model path, context size, threads, GPU layers, temperature)? Fix if needed.",
    },

    # ── Python ──
    "truth_audit_claim_check": {
        "name": "Truth-Audit - Claim Check",
        "category": "truth_audit",
        "difficulty": "medium",
        "text": (
            "Audit the following claims for factual reliability. For each claim, label it as likely true, likely false, mixed/uncertain, or unverifiable from the provided information. "
            "Explain the reason briefly and flag where external verification would be required.\n\n"
            "Claims:\n"
            "1. SQLite is a client-server database that requires a separate database daemon.\n"
            "2. FastAPI applications can expose JSON API endpoints and HTML responses.\n"
            "3. A larger LLM context size always guarantees higher answer quality.\n"
            "4. llama.cpp can expose OpenAI-compatible API endpoints through llama-server.\n"
            "5. GPU VRAM usage can be measured reliably on every GPU vendor with nvidia-smi."
        ),
        "self_validation_hint": "Review your audit. Did you avoid guessing? Did you mark unverifiable or mixed claims clearly? Did you explain why each claim is true, false, or uncertain? Improve if needed.",
        "checks": ["claim_labels", "uncertainty", "external_verification", "no_guessing"],
    },
    "truth_audit_contradiction_detection": {
        "name": "Truth-Audit - Contradiction Detection",
        "category": "truth_audit",
        "difficulty": "medium",
        "text": (
            "Find contradictions, unsupported statements, and risky assumptions in this short technical report. "
            "Return a structured audit with: contradiction, evidence from the text, why it matters, and a safer corrected statement.\n\n"
            "Report:\n"
            "The benchmark stores all results permanently, but each new run replaces older rows for the same model and prompt. "
            "The app has no database migrations, although it automatically adds missing columns at startup. "
            "The ranking is always based on the latest run only, yet it averages every historical row. "
            "Truth-Audit is fully implemented because the comparison page contains a chart for it."
        ),
        "self_validation_hint": "Review your contradiction audit. Did you refer to the exact conflicting statements? Did you separate contradictions from unsupported assumptions? Improve if needed.",
        "checks": ["contradictions", "unsupported_claims", "safer_statement", "structured_audit"],
    },
    "truth_audit_hallucination_resistance": {
        "name": "Truth-Audit - Hallucination Resistance",
        "category": "truth_audit",
        "difficulty": "hard",
        "text": (
            "Answer the questions below. If the answer is not knowable from the prompt, say that it cannot be determined from the provided information instead of inventing details.\n\n"
            "Context:\n"
            "A local benchmark app stores model results in SQLite. It has pages for Dashboard, Benchmark, Results, Ranking, and Comparisons. "
            "The Comparisons page can draw a separate Truth-Audit chart if matching results exist.\n\n"
            "Questions:\n"
            "1. Which exact model had the best Truth-Audit score?\n"
            "2. Does the app currently contain Truth-Audit prompts in its benchmark set?\n"
            "3. What database engine is mentioned?\n"
            "4. Name one UI page mentioned in the context.\n"
            "5. What should be shown if no Truth-Audit results exist?"
        ),
        "self_validation_hint": "Review your answers. Did you avoid inventing missing model names or scores? Did you distinguish what is stated from what is not stated? Improve if needed.",
        "checks": ["unknown_handling", "no_hallucination", "context_grounding", "direct_answers"],
    },

    "coding_python_sales_analysis": {
        "name": "Python — Data Processing",
        "category": "coding_language",
        "language": "python",
        "language_label": "Python",
        "difficulty": "medium",
        "text": "Write a Python function `analyze_sales(data)` that receives a list of dictionaries with `product`, `category`, `price`, and `quantity`. Calculate total revenue per category, return the top 3 products by revenue, ignore invalid rows with missing fields or negative values, use type hints, include a small example input/output, and explain time complexity.",
        "self_validation_hint": "Review your Python code. Does it handle edge cases? Are type hints used? Is invalid input handled? Improve if needed.",
        "checks": ["def", "type_hints", "dict", "invalid_rows", "sorting", "complexity"],
    },
    "coding_python_async_api_client": {
        "name": "Python — Async API Client",
        "category": "coding_language",
        "language": "python",
        "language_label": "Python",
        "difficulty": "medium",
        "text": "Write an async Python script that fetches JSON data from multiple URLs concurrently. Use `asyncio` and `aiohttp`, handle timeouts and HTTP errors, retry failed requests up to 3 times, and return successful results and failed URLs separately. Keep the code clean and production-ready.",
        "self_validation_hint": "Review your async code. Are timeouts set? Is error handling complete? Does retry work? Improve if needed.",
        "checks": ["asyncio", "aiohttp", "retry", "timeout", "http_errors", "separate_results"],
    },
    "coding_python_cli_largest_files": {
        "name": "Python — CLI Tool",
        "category": "coding_language",
        "language": "python",
        "language_label": "Python",
        "difficulty": "medium",
        "text": "Create a Python CLI tool that scans a folder and prints the 10 largest files. Use `argparse`, support recursive scanning, show file size in MB, handle permission errors safely, and sort results from largest to smallest.",
        "self_validation_hint": "Review your CLI tool. Does it handle errors? Is recursive scanning implemented? Improve if needed.",
        "checks": ["argparse", "recursive", "permission_errors", "sorting", "pathlib", "main_guard"],
    },

    # ── JavaScript ──
    "coding_javascript_group_orders": {
        "name": "JavaScript — Array/Object Logic",
        "category": "coding_language",
        "language": "javascript",
        "language_label": "JavaScript",
        "difficulty": "medium",
        "text": "Write a JavaScript function `groupOrdersByUser(orders)`. Input is an array of orders with `userId`, `amount`, and `status`. Group orders by user, calculate total paid amount per user, ignore cancelled orders, return users sorted by total amount descending, and include example input/output.",
        "self_validation_hint": "Review your JS code. Does it handle edge cases? Is grouping correct? Improve if needed.",
        "checks": ["function", "reduce", "grouping", "filter_cancelled", "sorting", "example"],
    },
    "coding_javascript_cached_fetch": {
        "name": "JavaScript — Async Fetch Cache",
        "category": "coding_language",
        "language": "javascript",
        "language_label": "JavaScript",
        "difficulty": "medium",
        "text": "Write a JavaScript function that fetches user data from an API and caches results. Use `fetch`, cache users by ID in memory, avoid duplicate network calls for the same user, handle failed requests, and use modern JavaScript syntax.",
        "self_validation_hint": "Review your cache. Does it deduplicate requests? Is error handling complete? Improve if needed.",
        "checks": ["fetch", "cache", "promise_dedup", "error_handling", "async", "modern_js"],
    },
    "coding_javascript_searchable_list": {
        "name": "JavaScript — DOM Component",
        "category": "coding_language",
        "language": "javascript",
        "language_label": "JavaScript",
        "difficulty": "medium",
        "text": "Create a small vanilla JavaScript component for a searchable list. Render a list of items, add an input field for search, filter results live while typing, highlight matching text, and do not use external libraries.",
        "self_validation_hint": "Review your DOM code. Is filtering live? Is highlighting correct? No external libraries? Improve if needed.",
        "checks": ["dom", "input_event", "filter", "highlight", "no_library", "render"],
    },

    # ── TypeScript ──
    "coding_typescript_invoice": {
        "name": "TypeScript — Strong Typing",
        "category": "coding_language",
        "language": "typescript",
        "language_label": "TypeScript",
        "difficulty": "medium",
        "text": "Write a TypeScript function `calculateInvoice(invoice)`. Define proper interfaces/types, support tax, discounts, and line items, prevent invalid values using type-safe checks, return subtotal, tax amount, discount amount, and final total, and include example usage.",
        "self_validation_hint": "Review your TypeScript. Are interfaces used? Is `any` avoided? Are types correct? Improve if needed.",
        "checks": ["interface", "types", "validation", "totals", "no_any", "example"],
    },
    "coding_typescript_api_response_validation": {
        "name": "TypeScript — API Response Validation",
        "category": "coding_language",
        "language": "typescript",
        "language_label": "TypeScript",
        "difficulty": "medium",
        "text": "Create a TypeScript utility that validates API responses. Define a generic `ApiResponse<T>` type, check success/error states, narrow types correctly, avoid using `any`, and include an example with a `User` object.",
        "self_validation_hint": "Review generics. Is type narrowing correct? Is `any` avoided? Improve if needed.",
        "checks": ["generic", "type_guard", "narrowing", "no_any", "ApiResponse", "example"],
    },
    "coding_typescript_state_manager": {
        "name": "TypeScript — State Manager",
        "category": "coding_language",
        "language": "typescript",
        "language_label": "TypeScript",
        "difficulty": "medium",
        "text": "Write a small TypeScript state manager. Support `getState`, `setState`, and `subscribe`, use generics, notify subscribers only when state changes, return an unsubscribe function, and include example usage.",
        "self_validation_hint": "Review your state manager. Is unsubscribe correct? Are subscribers notified properly? Improve if needed.",
        "checks": ["generic", "subscribe", "unsubscribe", "state_change", "types", "example"],
    },

    # ── Java ──
    "coding_java_user_service": {
        "name": "Java — Service Class",
        "category": "coding_language",
        "language": "java",
        "language_label": "Java",
        "difficulty": "medium",
        "text": "Write a Java class `UserService`. Add, remove, and find users by ID, prevent duplicate IDs, use proper encapsulation, use `Optional` where appropriate, and include a small `main` method for testing.",
        "self_validation_hint": "Review your Java class. Is encapsulation proper? Are Optional types used? Improve if needed.",
        "checks": ["class", "Optional", "encapsulation", "duplicate_check", "Map", "main"],
    },
    "coding_java_worker_executor": {
        "name": "Java — Multithreading",
        "category": "coding_language",
        "language": "java",
        "language_label": "Java",
        "difficulty": "medium",
        "text": "Write a Java program that processes a queue of tasks using multiple worker threads. Use `ExecutorService`, handle exceptions from tasks, shut down the executor safely, print completed and failed task counts, and avoid race conditions.",
        "self_validation_hint": "Review threading. Is shutdown safe? Are race conditions avoided? Improve if needed.",
        "checks": ["ExecutorService", "Callable_or_Runnable", "shutdown", "exceptions", "thread_safe_counts", "main"],
    },
    "coding_java_csv_inventory": {
        "name": "Java — File Parser",
        "category": "coding_language",
        "language": "java",
        "language_label": "Java",
        "difficulty": "medium",
        "text": "Write a Java program that reads a CSV file of products. Parse product name, price, and stock, skip invalid rows, calculate total inventory value, use try-with-resources, and keep the code clean and object-oriented.",
        "self_validation_hint": "Review CSV parsing. Is validation correct? Is try-with-resources used? Improve if needed.",
        "checks": ["csv", "try_with_resources", "validation", "BigDecimal_or_double", "class", "total"],
    },

    # ── C# ──
    "coding_csharp_linq_orders": {
        "name": "C# — LINQ Data Processing",
        "category": "coding_language",
        "language": "csharp",
        "language_label": "C#",
        "difficulty": "medium",
        "text": "Write a C# method that analyzes a list of orders. Use LINQ, group orders by customer, calculate total completed order amount, ignore cancelled orders, return the top 5 customers, and include model classes and example usage.",
        "self_validation_hint": "Review LINQ usage. Is groupby correct? Are top N correct? Improve if needed.",
        "checks": ["LINQ", "GroupBy", "Where", "OrderByDescending", "Take", "models"],
    },
    "coding_csharp_async_http_downloader": {
        "name": "C# — Async HTTP Client",
        "category": "coding_language",
        "language": "csharp",
        "language_label": "C#",
        "difficulty": "medium",
        "text": "Write a C# async method that downloads JSON from multiple URLs. Use `HttpClient`, `async`/`await`, handle timeouts and HTTP errors, return successful and failed results separately, and avoid blocking calls.",
        "self_validation_hint": "Review async C#. Are you using async/await properly? Any blocking calls? Improve if needed.",
        "checks": ["HttpClient", "async", "await", "timeout", "error_handling", "no_blocking"],
    },
    "coding_csharp_repository_pattern": {
        "name": "C# — Repository Pattern",
        "category": "coding_language",
        "language": "csharp",
        "language_label": "C#",
        "difficulty": "medium",
        "text": "Create a simple in-memory repository in C#. Use generics, support add, update, delete, and find by ID, use interfaces, handle missing items cleanly, and include example usage.",
        "self_validation_hint": "Review repository. Are interfaces used? Is generic pattern correct? Improve if needed.",
        "checks": ["interface", "generic", "repository", "CRUD", "missing_items", "example"],
    },

    # ── C++ ──
    "coding_cpp_transactions": {
        "name": "C++ — Modern C++ Data Processing",
        "category": "coding_language",
        "language": "cpp",
        "language_label": "C++",
        "difficulty": "medium",
        "text": "Write a C++17 program that analyzes a vector of transactions. Use structs/classes, calculate total amount per account, find the account with the highest balance, use `std::unordered_map`, handle invalid transactions, and include example input.",
        "self_validation_hint": "Review C++17. Are modern features used? Is memory safe? Improve if needed.",
        "checks": ["C++17", "struct", "std::vector", "std::unordered_map", "invalid", "main"],
    },
    "coding_cpp_raii_resource_manager": {
        "name": "C++ — Memory Safety",
        "category": "coding_language",
        "language": "cpp",
        "language_label": "C++",
        "difficulty": "medium",
        "text": "Write a C++ program that implements a small resource manager. Use RAII, avoid raw owning pointers, use smart pointers where appropriate, demonstrate construction/destruction, and explain why the implementation is memory-safe.",
        "self_validation_hint": "Review RAII. Are smart pointers used? Are raw owning pointers avoided? Improve if needed.",
        "checks": ["RAII", "unique_ptr_or_shared_ptr", "destructor", "no_raw_owning_pointer", "class", "memory_safe"],
    },
    "coding_cpp_longest_unique_substring": {
        "name": "C++ — Algorithm Task",
        "category": "coding_language",
        "language": "cpp",
        "language_label": "C++",
        "difficulty": "medium",
        "text": "Write a C++ function that finds the longest substring without repeating characters. Use an efficient sliding-window algorithm, return both the substring and its length, handle UTF-8 input only as bytes, explain time and space complexity, and include test cases.",
        "self_validation_hint": "Review algorithm. Is sliding window efficient? Are edge cases handled? Improve if needed.",
        "checks": ["sliding_window", "unordered_map_or_set", "pair_or_struct", "tests", "complexity", "edge_cases"],
    },

    # ── C ──
    "coding_c_integer_parser": {
        "name": "C — String Parser",
        "category": "coding_language",
        "language": "c",
        "language_label": "C",
        "difficulty": "medium",
        "text": "Write a C program that parses a comma-separated string of integers. Convert valid numbers into an array, ignore invalid tokens, avoid buffer overflows, use dynamic memory safely, and free all allocated memory.",
        "self_validation_hint": "Review C. Is memory properly freed? Are bounds checked? Improve if needed.",
        "checks": ["malloc", "free", "strtol", "bounds", "invalid_tokens", "main"],
    },
    "coding_c_file_statistics": {
        "name": "C — File Statistics",
        "category": "coding_language",
        "language": "c",
        "language_label": "C",
        "difficulty": "medium",
        "text": "Write a C program that reads a text file and prints statistics. Count lines, words, and characters, handle missing files, work with large files, avoid unsafe string functions, and return proper exit codes.",
        "self_validation_hint": "Review C file I/O. Is error handling complete? Are unsafe functions avoided? Improve if needed.",
        "checks": ["fopen", "fgetc_or_fread", "exit_codes", "large_file", "error_handling", "no_gets"],
    },
    "coding_c_hash_table": {
        "name": "C — Simple Hash Table",
        "category": "coding_language",
        "language": "c",
        "language_label": "C",
        "difficulty": "medium",
        "text": "Implement a simple hash table in C. Support string keys and integer values, implement insert, get, and delete, handle collisions, manage memory correctly, and include a small test in `main`.",
        "self_validation_hint": "Review hash table. Are collisions handled? Is memory freed? Improve if needed.",
        "checks": ["struct", "hash", "collision", "insert", "delete", "free"],
    },

    # ── Go ──
    "coding_go_worker_pool": {
        "name": "Go — Concurrent Worker Pool",
        "category": "coding_language",
        "language": "go",
        "language_label": "Go",
        "difficulty": "medium",
        "text": "Write a Go program that processes jobs with a worker pool. Use goroutines and channels, support configurable worker count, collect successful and failed jobs, avoid goroutine leaks, and include example usage.",
        "self_validation_hint": "Review Go code. Are goroutine leaks avoided? Is channel usage correct? Improve if needed.",
        "checks": ["goroutine", "channel", "worker_pool", "WaitGroup", "errors", "no_leak"],
    },
    "coding_go_http_task_server": {
        "name": "Go — HTTP API Server",
        "category": "coding_language",
        "language": "go",
        "language_label": "Go",
        "difficulty": "medium",
        "text": "Write a small Go HTTP server. Provide endpoints for creating and listing tasks, use JSON request/response bodies, validate input, return proper HTTP status codes, and use only the standard library.",
        "self_validation_hint": "Review HTTP server. Are status codes correct? Is input validated? Improve if needed.",
        "checks": ["net/http", "json", "handlers", "status_codes", "validation", "stdlib"],
    },
    "coding_go_log_parser": {
        "name": "Go — Log Parser",
        "category": "coding_language",
        "language": "go",
        "language_label": "Go",
        "difficulty": "medium",
        "text": "Write a Go function that parses web server logs. Extract IP, timestamp, method, path, and status code, count requests per status code, ignore malformed lines, and include unit-test-like examples.",
        "self_validation_hint": "Review log parser. Are malformed lines handled? Is counting correct? Improve if needed.",
        "checks": ["regexp_or_strings", "struct", "map", "malformed", "tests", "status_count"],
    },

    # ── Rust ──
    "coding_rust_word_frequency": {
        "name": "Rust — Ownership and Error Handling",
        "category": "coding_language",
        "language": "rust",
        "language_label": "Rust",
        "difficulty": "medium",
        "text": "Write a Rust function that reads a file and counts word frequency. Use `Result` for error handling, avoid unnecessary cloning, use `HashMap`, return the top 10 words, and include example usage.",
        "self_validation_hint": "Review Rust. Is ownership correct? Is error handling idiomatic? Improve if needed.",
        "checks": ["Result", "HashMap", "BufRead", "ownership", "sort", "error_handling"],
    },
    "coding_rust_cli_line_filter": {
        "name": "Rust — CLI Parser",
        "category": "coding_language",
        "language": "rust",
        "language_label": "Rust",
        "difficulty": "medium",
        "text": "Write a Rust CLI program that filters lines from a file. Accept file path and search term as arguments, print matching lines with line numbers, handle file errors properly, use idiomatic Rust, and avoid panics for normal errors.",
        "self_validation_hint": "Review CLI Rust. Are errors handled with Result? No panics? Improve if needed.",
        "checks": ["env_args", "Result", "BufReader", "enumerate", "no_panic", "main"],
    },
    "coding_rust_shape_trait": {
        "name": "Rust — Struct and Traits",
        "category": "coding_language",
        "language": "rust",
        "language_label": "Rust",
        "difficulty": "medium",
        "text": "Create a Rust trait `Shape`. Implement it for `Circle` and `Rectangle`, provide area and perimeter methods, store multiple shapes in a vector, print total area, and use dynamic dispatch correctly.",
        "self_validation_hint": "Review traits. Is dynamic dispatch correct? Are methods implemented? Improve if needed.",
        "checks": ["trait", "struct", "impl", "Box<dyn", "Vec", "methods"],
    },

    # ── PHP ──
    "coding_php_form_validation": {
        "name": "PHP — Form Validation",
        "category": "coding_language",
        "language": "php",
        "language_label": "PHP",
        "difficulty": "medium",
        "text": "Write a PHP function that validates registration form data. Validate email, username, and password, return structured errors, sanitize output, do not store plain-text passwords, and include example input/output.",
        "self_validation_hint": "Review PHP. Is password hashed? Is sanitization done? Improve if needed.",
        "checks": ["filter_var", "password_hash", "errors", "sanitize", "strict_types", "example"],
    },
    "coding_php_router": {
        "name": "PHP — Simple Router",
        "category": "coding_language",
        "language": "php",
        "language_label": "PHP",
        "difficulty": "medium",
        "text": "Create a small PHP router. Support GET and POST routes, match dynamic parameters like `/users/{id}`, return 404 for unknown routes, keep the implementation dependency-free, and include example routes.",
        "self_validation_hint": "Review router. Are dynamic params handled? Is 404 returned? Improve if needed.",
        "checks": ["class", "GET", "POST", "dynamic_params", "404", "no_dependency"],
    },
    "coding_php_pdo_database": {
        "name": "PHP — Database Layer",
        "category": "coding_language",
        "language": "php",
        "language_label": "PHP",
        "difficulty": "medium",
        "text": "Write a PHP class for database access using PDO. Use prepared statements, support fetching users by ID, handle database errors safely, avoid SQL injection, and include example usage.",
        "self_validation_hint": "Review PDO. Are prepared statements used? Is SQL injection prevented? Improve if needed.",
        "checks": ["PDO", "prepare", "execute", "try_catch", "findById", "sql_injection_safe"],
    },

    # ── Ruby ──
    "coding_ruby_expense_grouping": {
        "name": "Ruby — Data Transformation",
        "category": "coding_language",
        "language": "ruby",
        "language_label": "Ruby",
        "difficulty": "medium",
        "text": "Write a Ruby method that groups expenses by category. Input is an array of hashes, calculate total amount per category, ignore invalid expenses, sort categories by total descending, and include example input/output.",
        "self_validation_hint": "Review Ruby. Is grouping correct? Is sorting correct? Improve if needed.",
        "checks": ["def", "hash", "grouping", "validation", "sort_by", "example"],
    },
    "coding_ruby_file_renamer": {
        "name": "Ruby — CLI Script",
        "category": "coding_language",
        "language": "ruby",
        "language_label": "Ruby",
        "difficulty": "medium",
        "text": "Write a Ruby CLI script that renames files in a folder. Accept folder path and prefix, rename files safely, avoid overwriting existing files, print a summary, and handle errors cleanly.",
        "self_validation_hint": "Review Ruby CLI. Are file operations safe? Is overwriting prevented? Improve if needed.",
        "checks": ["ARGV", "File", "rename", "exist_check", "errors", "summary"],
    },
    "coding_ruby_todo_list": {
        "name": "Ruby — Class Design",
        "category": "coding_language",
        "language": "ruby",
        "language_label": "Ruby",
        "difficulty": "medium",
        "text": "Create a Ruby class `TodoList`. Add, complete, delete, and list tasks, track task status, prevent empty task titles, include example usage, and keep the API simple.",
        "self_validation_hint": "Review class. Is API clean? Is validation done? Improve if needed.",
        "checks": ["class", "initialize", "methods", "validation", "status", "example"],
    },

    # ── Kotlin ──
    "coding_kotlin_product_manager": {
        "name": "Kotlin — Data Classes",
        "category": "coding_language",
        "language": "kotlin",
        "language_label": "Kotlin",
        "difficulty": "medium",
        "text": "Write a Kotlin program that manages a list of products. Use data classes, filter products by availability, calculate total stock value, sort products by price, and include example usage.",
        "self_validation_hint": "Review Kotlin. Are data classes used? Is null-safety handled? Improve if needed.",
        "checks": ["data class", "filter", "sumOf", "sortedBy", "nullable_safe", "main"],
    },
    "coding_kotlin_coroutines_loader": {
        "name": "Kotlin — Coroutines",
        "category": "coding_language",
        "language": "kotlin",
        "language_label": "Kotlin",
        "difficulty": "medium",
        "text": "Write a Kotlin function that loads data from multiple sources concurrently. Use coroutines, handle failed requests, return successful and failed results, avoid blocking calls, and include clear error handling.",
        "self_validation_hint": "Review coroutines. Is coroutine scope correct? Are blocking calls avoided? Improve if needed.",
        "checks": ["suspend", "coroutineScope", "async", "awaitAll", "Result", "no_blocking"],
    },
    "coding_kotlin_null_safe_profile": {
        "name": "Kotlin — Null Safety",
        "category": "coding_language",
        "language": "kotlin",
        "language_label": "Kotlin",
        "difficulty": "medium",
        "text": "Write a Kotlin function that processes user profiles. Use nullable types correctly, avoid unsafe `!!`, provide default values where needed, return a clean display name, and include test cases.",
        "self_validation_hint": "Review null safety. Are nullable types handled? Is `!!` avoided? Improve if needed.",
        "checks": ["nullable", "?:", "no_double_bang", "data class", "tests", "display_name"],
    },

    # ── Swift ──
    "coding_swift_book_filter": {
        "name": "Swift — Model and Filtering",
        "category": "coding_language",
        "language": "swift",
        "language_label": "Swift",
        "difficulty": "medium",
        "text": "Write a Swift function that filters and sorts a list of books. Use structs, filter by genre and minimum rating, sort by rating descending, return formatted book titles, and include example usage.",
        "self_validation_hint": "Review Swift. Are structs used? Is filtering correct? Improve if needed.",
        "checks": ["struct", "filter", "sorted", "map", "example", "types"],
    },
    "coding_swift_async_json_fetch": {
        "name": "Swift — Async/Await",
        "category": "coding_language",
        "language": "swift",
        "language_label": "Swift",
        "difficulty": "medium",
        "text": "Write a Swift async function that fetches JSON from an API. Use `async/await`, decode JSON into Codable structs, handle network and decoding errors, return a typed result, and include example usage.",
        "self_validation_hint": "Review async Swift. Is Codable used? Are errors handled? Improve if needed.",
        "checks": ["async", "await", "Codable", "URLSession", "do_catch", "typed_result"],
    },
    "coding_swift_payable_protocol": {
        "name": "Swift — Protocols",
        "category": "coding_language",
        "language": "swift",
        "language_label": "Swift",
        "difficulty": "medium",
        "text": "Create a Swift protocol `Payable`. Implement it for `Employee` and `Contractor`, calculate monthly payment, store different payable objects in one array, print total monthly cost, and use idiomatic Swift.",
        "self_validation_hint": "Review protocols. Is protocol conformance correct? Is polymorphism used? Improve if needed.",
        "checks": ["protocol", "struct_or_class", "implementation", "array", "reduce", "example"],
    },

    # ── Dart ──
    "coding_dart_task_processing": {
        "name": "Dart — List Processing",
        "category": "coding_language",
        "language": "dart",
        "language_label": "Dart",
        "difficulty": "medium",
        "text": "Write a Dart function that processes a list of tasks. Filter completed and pending tasks, sort by due date, return a summary object, use classes or data models, and include example usage.",
        "self_validation_hint": "Review Dart. Are list operations correct? Is sorting correct? Improve if needed.",
        "checks": ["class", "List", "where", "sort", "DateTime", "summary"],
    },
    "coding_dart_async_resource_loader": {
        "name": "Dart — Async Future Handling",
        "category": "coding_language",
        "language": "dart",
        "language_label": "Dart",
        "difficulty": "medium",
        "text": "Write a Dart function that loads multiple resources asynchronously. Use `Future`, handle failed resources, return successful and failed results separately, avoid blocking code, and include example usage.",
        "self_validation_hint": "Review async Dart. Are Futures handled correctly? Is error handling complete? Improve if needed.",
        "checks": ["Future", "async", "await", "try_catch", "separate_results", "no_blocking"],
    },
    "coding_dart_flutter_task_card": {
        "name": "Dart — Flutter Widget",
        "category": "coding_language",
        "language": "dart",
        "language_label": "Dart",
        "difficulty": "medium",
        "text": "Create a simple Flutter widget for a task card. Show title, description, and status, use proper widget composition, support completed and pending states, keep styling clean, and do not use external packages.",
        "self_validation_hint": "Review Flutter widget. Is composition correct? Are states handled? Improve if needed.",
        "checks": ["Widget", "StatelessWidget", "build", "Text", "Container_or_Card", "no_package"],
    },

    # ── SQL ──
    "coding_sql_sales_query": {
        "name": "SQL — Sales Query",
        "category": "coding_language",
        "language": "sql",
        "language_label": "SQL",
        "difficulty": "medium",
        "text": "Write SQL queries for tables `orders(id, customer_id, status, created_at)`, `order_items(id, order_id, product_id, quantity, price)`, and `customers(id, name)`. Calculate total revenue per customer, include only completed orders, return the top 10 customers with customer name and revenue, and sort by revenue descending.",
        "self_validation_hint": "Review SQL. Are JOINs correct? Is revenue calculated correctly? Improve if needed.",
        "checks": ["SELECT", "JOIN", "SUM", "GROUP BY", "WHERE", "ORDER BY"],
    },
    "coding_sql_duplicate_users": {
        "name": "SQL — Duplicate Detection",
        "category": "coding_language",
        "language": "sql",
        "language_label": "SQL",
        "difficulty": "medium",
        "text": "Write a SQL query for table `users(id, email, created_at)`. Find emails used by more than one user, return email, duplicate count, first created date, and last created date, and sort by duplicate count descending.",
        "self_validation_hint": "Review SQL. Are duplicates detected correctly? Is HAVING used? Improve if needed.",
        "checks": ["SELECT", "COUNT", "GROUP BY", "HAVING", "MIN", "MAX"],
    },
    "coding_sql_monthly_report": {
        "name": "SQL — Monthly Report",
        "category": "coding_language",
        "language": "sql",
        "language_label": "SQL",
        "difficulty": "medium",
        "text": "Write a SQL query for monthly revenue. Group completed orders by month, calculate revenue and order count, include months with zero revenue if possible, explain assumptions, and keep the query readable.",
        "self_validation_hint": "Review SQL. Is monthly grouping correct? Are zero-revenue months included? Improve if needed.",
        "checks": ["date_grouping", "SUM", "COUNT", "LEFT JOIN_or_series", "completed", "explanation"],
    },

    # ── Bash ──
    "coding_bash_backup_script": {
        "name": "Bash — Backup Script",
        "category": "coding_language",
        "language": "bash",
        "language_label": "Bash",
        "difficulty": "medium",
        "text": "Write a Bash script that creates backups of a folder. Accept source and destination paths, create timestamped archive files, check if source exists, delete backups older than 14 days, and print clear status messages.",
        "self_validation_hint": "Review Bash. Is error handling complete? Are paths safe? Improve if needed.",
        "checks": ["set -euo pipefail", "tar", "timestamp", "validation", "find", "quoting"],
    },
    "coding_bash_log_scanner": {
        "name": "Bash — Log Scanner",
        "category": "coding_language",
        "language": "bash",
        "language_label": "Bash",
        "difficulty": "medium",
        "text": "Write a Bash script that scans log files for errors. Search recursively, count errors per file, print the top 10 files with most errors, handle spaces in filenames, and use safe shell practices.",
        "self_validation_hint": "Review Bash. Are spaces in filenames handled? Is quoting correct? Improve if needed.",
        "checks": ["find", "grep", "sort", "head", "quoting", "strict_mode"],
    },
    "coding_bash_process_monitor": {
        "name": "Bash — Process Monitor",
        "category": "coding_language",
        "language": "bash",
        "language_label": "Bash",
        "difficulty": "medium",
        "text": "Write a Bash script that checks if a process is running. Accept process name as argument, print status, restart the process using a command if it is not running, write actions to a log file, and validate all inputs.",
        "self_validation_hint": "Review Bash. Is input validated? Is logging correct? Improve if needed.",
        "checks": ["pgrep", "restart", "logging", "args", "validation", "exit_codes"],
    },

    # ── PowerShell ──
    "coding_powershell_system_report": {
        "name": "PowerShell — System Report",
        "category": "coding_language",
        "language": "powershell",
        "language_label": "PowerShell",
        "difficulty": "medium",
        "text": "Write a PowerShell script that creates a system report. Show CPU, RAM, disk usage, and OS version, export results to JSON, handle permission errors, keep output readable, and use proper PowerShell cmdlets.",
        "self_validation_hint": "Review PowerShell. Are cmdlets used correctly? Is JSON export correct? Improve if needed.",
        "checks": ["Get-CimInstance", "Get-PSDrive", "ConvertTo-Json", "try_catch", "parameters", "output"],
    },
    "coding_powershell_file_cleanup": {
        "name": "PowerShell — File Cleanup",
        "category": "coding_language",
        "language": "powershell",
        "language_label": "PowerShell",
        "difficulty": "medium",
        "text": "Write a PowerShell script that deletes old temporary files. Accept folder path and max file age in days, show what will be deleted before deleting, support a dry-run mode, handle locked files, and print a summary.",
        "self_validation_hint": "Review PowerShell. Is dry-run supported? Are errors handled? Improve if needed.",
        "checks": ["param", "Get-ChildItem", "Where-Object", "WhatIf_or_DryRun", "Remove-Item", "summary"],
    },
    "coding_powershell_service_checker": {
        "name": "PowerShell — Service Checker",
        "category": "coding_language",
        "language": "powershell",
        "language_label": "PowerShell",
        "difficulty": "medium",
        "text": "Write a PowerShell script that checks Windows services. Accept a list of service names, show running/stopped status, restart stopped services if requested, log all actions, and handle missing services cleanly.",
        "self_validation_hint": "Review PowerShell. Are missing services handled? Is logging correct? Improve if needed.",
        "checks": ["Get-Service", "Restart-Service", "param", "logging", "missing_service", "switch"],
    },

    # ── Engine: Vulkan ──
    "engine_vulkan_triangle_swapchain": {
        "name": "Vulkan — Triangle, Swapchain and Synchronization",
        "category": "game_engine",
        "engine_skill": "vulkan",
        "engine_skill_label": "Vulkan",
        "difficulty": "hard",
        "text": "Write a minimal Vulkan renderer in C++ that opens a window and renders a colored triangle. Explain the required Vulkan objects and show the core code structure.\n\nRequirements:\n- Create instance, physical device, logical device, surface and swapchain.\n- Create image views, render pass, graphics pipeline and framebuffers.\n- Record command buffers for drawing a triangle.\n- Use semaphores and fences correctly for frames in flight.\n- Enable validation layers in debug builds.\n- Explain the purpose of each synchronization object.\n- Keep the code structured into initialization, draw loop and cleanup sections.",
        "self_validation_hint": "Review your Vulkan code. Are all synchronization objects used correctly? Are validation layers enabled? Improve if needed.",
        "checks": ["instance", "physical_device", "logical_device", "swapchain", "render_pass", "pipeline", "command_buffer", "semaphore", "fence", "validation_layers", "cleanup"],
    },
    "engine_vulkan_texture_upload": {
        "name": "Vulkan — Texture Upload and Layout Transitions",
        "category": "game_engine",
        "engine_skill": "vulkan",
        "engine_skill_label": "Vulkan",
        "difficulty": "hard",
        "text": "Write C++ Vulkan code and explanation for uploading a 2D texture from CPU memory to the GPU.\n\nRequirements:\n- Use a staging buffer.\n- Allocate device-local image memory.\n- Copy buffer data into the image.\n- Perform correct image layout transitions.\n- Create image view and sampler.\n- Explain transfer queue usage if available.\n- Include common mistakes that cause black textures.",
        "self_validation_hint": "Review your texture upload. Are layout transitions correct? Is staging buffer used? Improve if needed.",
        "checks": ["staging_buffer", "device_local", "vkCmdCopyBufferToImage", "layout_transition", "image_view", "sampler", "barrier", "black_texture_debugging"],
    },
    "engine_vulkan_descriptor_sets": {
        "name": "Vulkan — Descriptor Sets and Uniform Buffers",
        "category": "game_engine",
        "engine_skill": "vulkan",
        "engine_skill_label": "Vulkan",
        "difficulty": "hard",
        "text": "Design and implement the descriptor system for a Vulkan renderer that uses per-frame uniform buffers and combined image samplers.\n\nRequirements:\n- Create descriptor set layout.\n- Create descriptor pool.\n- Allocate descriptor sets for multiple frames in flight.\n- Bind uniform buffers and texture samplers.\n- Update descriptors safely.\n- Explain why descriptor sets are not the same as OpenGL global state.\n- Include C++ code snippets.",
        "self_validation_hint": "Review descriptor system. Are descriptors updated safely? Is frames-in-flight handled? Improve if needed.",
        "checks": ["descriptor_set_layout", "descriptor_pool", "allocate_descriptor_sets", "uniform_buffer", "combined_image_sampler", "frames_in_flight", "vkUpdateDescriptorSets"],
    },
    "engine_vulkan_synchronization_debug": {
        "name": "Vulkan — Synchronization Bug Fix",
        "category": "game_engine",
        "engine_skill": "vulkan",
        "engine_skill_label": "Vulkan",
        "difficulty": "hard",
        "text": "A Vulkan renderer sometimes flickers, sometimes shows old frames, and validation layers report possible hazards around image layout transitions. Diagnose the likely synchronization problems and provide a corrected synchronization strategy.\n\nRequirements:\n- Explain execution dependency vs memory dependency.\n- Use pipeline barriers correctly.\n- Explain image layout transitions.\n- Use acquire/present semaphores correctly.\n- Use fences for CPU/GPU frame pacing.\n- Mention how to verify the fix with validation layers and RenderDoc.",
        "self_validation_hint": "Review synchronization strategy. Are barriers correct? Is RenderDoc mentioned? Improve if needed.",
        "checks": ["execution_dependency", "memory_dependency", "pipeline_barrier", "image_layout", "acquire_semaphore", "present_semaphore", "fence", "RenderDoc"],
    },

    # ── Engine: GLSL ──
    "engine_glsl_pbr_fragment_shader": {
        "name": "GLSL — PBR Fragment Shader",
        "category": "game_engine",
        "engine_skill": "glsl",
        "engine_skill_label": "GLSL",
        "difficulty": "hard",
        "text": "Write a GLSL fragment shader for physically based rendering using metallic-roughness workflow.\n\nRequirements:\n- Use albedo, normal, metallic, roughness and ambient occlusion inputs.\n- Implement Cook-Torrance BRDF with GGX distribution.\n- Include Fresnel-Schlick and geometry term.\n- Support at least one directional light.\n- Apply gamma correction.\n- Explain assumptions and limitations.",
        "self_validation_hint": "Review PBR shader. Is Cook-Torrance BRDF correct? Is gamma correction applied? Improve if needed.",
        "checks": ["GLSL", "Cook-Torrance", "GGX", "Fresnel", "metallic", "roughness", "normal", "gamma_correction", "directional_light"],
    },
    "engine_glsl_normal_mapping": {
        "name": "GLSL — Tangent Space Normal Mapping",
        "category": "game_engine",
        "engine_skill": "glsl",
        "engine_skill_label": "GLSL",
        "difficulty": "hard",
        "text": "Write a GLSL vertex and fragment shader pair for tangent-space normal mapping.\n\nRequirements:\n- Pass position, normal, tangent and UV from vertex shader.\n- Build a TBN matrix.\n- Sample a normal map.\n- Convert sampled normal from texture space to tangent/world space.\n- Use the normal in lighting.\n- Explain common bugs such as inverted green channel or wrong tangent basis.",
        "self_validation_hint": "Review normal mapping. Is TBN matrix correct? Is inverted green channel discussed? Improve if needed.",
        "checks": ["vertex_shader", "fragment_shader", "TBN", "tangent", "bitangent", "normal_map", "texture_space", "lighting", "inverted_green"],
    },
    "engine_glsl_shadow_mapping": {
        "name": "GLSL — Shadow Mapping",
        "category": "game_engine",
        "engine_skill": "glsl",
        "engine_skill_label": "GLSL",
        "difficulty": "hard",
        "text": "Write GLSL shaders and rendering steps for basic shadow mapping.\n\nRequirements:\n- Create a depth pass from the light point of view.\n- Sample the shadow map in the lighting pass.\n- Transform world position into light clip space.\n- Apply bias to reduce shadow acne.\n- Implement PCF filtering.\n- Explain peter-panning and acne tradeoffs.",
        "self_validation_hint": "Review shadow mapping. Is bias correct? Is PCF implemented? Improve if needed.",
        "checks": ["depth_pass", "light_space_matrix", "shadow_map", "bias", "PCF", "shadow_acne", "peter_panning"],
    },
    "engine_glsl_compute_particles": {
        "name": "GLSL — Compute Shader Particle Simulation",
        "category": "game_engine",
        "engine_skill": "glsl",
        "engine_skill_label": "GLSL",
        "difficulty": "hard",
        "text": "Write a GLSL compute shader that updates a particle system on the GPU.\n\nRequirements:\n- Use shader storage buffer objects.\n- Update position and velocity.\n- Apply gravity and lifetime.\n- Respawn dead particles.\n- Use work group size correctly.\n- Explain synchronization requirements between compute and render passes.",
        "self_validation_hint": "Review compute shader. Is work group size set? Are memory barriers used? Improve if needed.",
        "checks": ["compute_shader", "SSBO", "work_group_size", "position", "velocity", "lifetime", "respawn", "memory_barrier"],
    },

    # ── Engine: HLSL / DirectX ──
    "engine_hlsl_lighting_shader": {
        "name": "HLSL — Blinn-Phong Lighting Shader",
        "category": "game_engine",
        "engine_skill": "hlsl",
        "engine_skill_label": "HLSL",
        "difficulty": "hard",
        "text": "Write an HLSL vertex and pixel shader for textured Blinn-Phong lighting.\n\nRequirements:\n- Use constant buffers for matrices and light data.\n- Sample a diffuse texture.\n- Calculate ambient, diffuse and specular lighting.\n- Use normal transformation correctly.\n- Explain register bindings.\n- Include shader code and a short pipeline explanation.",
        "self_validation_hint": "Review HLSL shader. Are register bindings explained? Is normal transform correct? Improve if needed.",
        "checks": ["cbuffer", "Texture2D", "SamplerState", "vertex_shader", "pixel_shader", "Blinn-Phong", "register", "normal_transform"],
    },
    "engine_directx12_resource_barriers": {
        "name": "DirectX 12 — Resource Barriers",
        "category": "game_engine",
        "engine_skill": "directx12",
        "engine_skill_label": "DirectX 12",
        "difficulty": "hard",
        "text": "Explain and implement DirectX 12 resource state transitions for rendering to a texture and then sampling it in a post-processing pass.\n\nRequirements:\n- Explain resource states.\n- Transition render target to shader resource.\n- Use command lists correctly.\n- Mention descriptor heaps.\n- Show pseudo-code or C++ snippets.\n- Explain common mistakes that cause GPU validation errors.",
        "self_validation_hint": "Review DX12 barriers. Are resource states correct? Are descriptor heaps mentioned? Improve if needed.",
        "checks": ["D3D12_RESOURCE_STATE_RENDER_TARGET", "D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE", "ResourceBarrier", "command_list", "descriptor_heap", "validation"],
    },

    # ── Engine: OpenGL ──
    "engine_opengl_deferred_renderer": {
        "name": "OpenGL — Deferred Rendering",
        "category": "game_engine",
        "engine_skill": "opengl",
        "engine_skill_label": "OpenGL",
        "difficulty": "hard",
        "text": "Design an OpenGL deferred renderer.\n\nRequirements:\n- Create a G-buffer with position, normal, albedo and material data.\n- Write geometry pass shaders.\n- Write lighting pass logic.\n- Explain framebuffer setup.\n- Explain how to handle depth, transparency and MSAA limitations.\n- Include code snippets for framebuffer and texture attachments.",
        "self_validation_hint": "Review deferred renderer. Is G-buffer complete? Are MSAA limitations discussed? Improve if needed.",
        "checks": ["G-buffer", "framebuffer", "texture_attachment", "geometry_pass", "lighting_pass", "depth", "transparency", "MSAA"],
    },
    "engine_opengl_instancing": {
        "name": "OpenGL — Instanced Rendering",
        "category": "game_engine",
        "engine_skill": "opengl",
        "engine_skill_label": "OpenGL",
        "difficulty": "hard",
        "text": "Write an OpenGL example for rendering thousands of identical meshes using instancing.\n\nRequirements:\n- Use vertex array objects and vertex buffer objects.\n- Upload per-instance transform data.\n- Use glVertexAttribDivisor.\n- Draw with glDrawElementsInstanced or glDrawArraysInstanced.\n- Explain performance benefits and limitations.",
        "self_validation_hint": "Review instancing. Is glVertexAttribDivisor used? Are performance benefits explained? Improve if needed.",
        "checks": ["VAO", "VBO", "instance_buffer", "glVertexAttribDivisor", "glDrawElementsInstanced", "transform", "performance"],
    },

    # ── Engine: WebGPU ──
    "engine_webgpu_triangle_wgsl": {
        "name": "WebGPU — Triangle with WGSL",
        "category": "game_engine",
        "engine_skill": "webgpu",
        "engine_skill_label": "WebGPU",
        "difficulty": "hard",
        "text": "Write a minimal WebGPU example that renders a triangle using WGSL shaders.\n\nRequirements:\n- Request adapter and device.\n- Configure canvas context.\n- Create render pipeline.\n- Write WGSL vertex and fragment shaders.\n- Encode commands and submit them.\n- Explain how WebGPU differs from WebGL.",
        "self_validation_hint": "Review WebGPU code. Is WGSL used? Is WebGL difference explained? Improve if needed.",
        "checks": ["adapter", "device", "canvas_context", "render_pipeline", "WGSL", "command_encoder", "submit", "WebGL_difference"],
    },

    # ── Engine: Render Pipeline ──
    "engine_render_forward_plus": {
        "name": "Render Pipeline — Forward+ Renderer Design",
        "category": "game_engine",
        "engine_skill": "render_pipeline",
        "engine_skill_label": "Rendering",
        "difficulty": "hard",
        "text": "Design a Forward+ renderer for a 3D game engine.\n\nRequirements:\n- Explain depth pre-pass.\n- Divide the screen into tiles or clusters.\n- Cull lights on the GPU.\n- Store visible lights per tile or cluster.\n- Perform lighting in the main pass.\n- Compare Forward+ against classic forward and deferred rendering.\n- Include data structures and pass order.",
        "self_validation_hint": "Review Forward+ design. Is light culling explained? Is comparison with deferred included? Improve if needed.",
        "checks": ["depth_prepass", "tiles", "clusters", "light_culling", "compute_shader", "visible_lights", "forward_vs_deferred", "pass_order"],
    },
    "engine_render_graph": {
        "name": "Render Pipeline — Render Graph Architecture",
        "category": "game_engine",
        "engine_skill": "render_pipeline",
        "engine_skill_label": "Rendering",
        "difficulty": "hard",
        "text": "Design a render graph system for a custom game engine.\n\nRequirements:\n- Represent passes, resources and dependencies.\n- Automatically order passes.\n- Track texture/resource lifetimes.\n- Insert synchronization barriers conceptually.\n- Allow transient resources.\n- Provide pseudo-code for adding a shadow pass, geometry pass, lighting pass and post-processing pass.",
        "self_validation_hint": "Review render graph. Is topological sort mentioned? Are transient resources supported? Improve if needed.",
        "checks": ["render_graph", "passes", "resources", "dependencies", "topological_sort", "resource_lifetime", "barriers", "transient_resources"],
    },
    "engine_render_hdr_postprocessing": {
        "name": "Render Pipeline — HDR and Post-Processing",
        "category": "game_engine",
        "engine_skill": "render_pipeline",
        "engine_skill_label": "Rendering",
        "difficulty": "hard",
        "text": "Design an HDR rendering and post-processing pipeline.\n\nRequirements:\n- Render scene into HDR color buffer.\n- Apply bloom extraction and blur.\n- Apply tone mapping.\n- Apply gamma correction at the correct stage.\n- Explain sRGB versus linear color space.\n- Include pass order and texture formats.",
        "self_validation_hint": "Review HDR pipeline. Is tone mapping correct? Is sRGB vs linear explained? Improve if needed.",
        "checks": ["HDR", "bloom", "blur", "tone_mapping", "gamma_correction", "linear_color", "sRGB", "texture_format", "pass_order"],
    },

    # ── Engine: Shader Debugging ──
    "engine_shader_black_screen_debug": {
        "name": "Shader Debugging — Black Screen",
        "category": "game_engine",
        "engine_skill": "shader_debugging",
        "engine_skill_label": "Shader",
        "difficulty": "hard",
        "text": "A custom engine shows a black screen after adding a new shader pipeline. Give a systematic debugging plan.\n\nRequirements:\n- Check shader compilation and linking.\n- Check vertex input layout.\n- Check uniforms/descriptors.\n- Check depth test and culling.\n- Check render target format.\n- Check camera matrices.\n- Explain how to use RenderDoc to inspect the frame.\n- Prioritize likely causes.",
        "self_validation_hint": "Review debugging plan. Is RenderDoc mentioned? Are all checks prioritized? Improve if needed.",
        "checks": ["shader_compile", "vertex_layout", "uniforms", "descriptors", "depth_test", "culling", "render_target", "camera_matrix", "RenderDoc"],
    },
    "engine_shader_wrong_normals_debug": {
        "name": "Shader Debugging — Wrong Lighting / Normals",
        "category": "game_engine",
        "engine_skill": "shader_debugging",
        "engine_skill_label": "Shader",
        "difficulty": "hard",
        "text": "A 3D model renders with broken lighting: one side is too dark, normal maps look inverted, and rotating the model changes highlights incorrectly. Diagnose the likely causes and propose fixes.\n\nRequirements:\n- Discuss normal matrix.\n- Discuss tangent space and TBN correctness.\n- Discuss handedness and bitangent sign.\n- Discuss sRGB/linear issues for normal maps.\n- Discuss imported mesh tangents.\n- Provide shader-level and asset-pipeline fixes.",
        "self_validation_hint": "Review normal debugging. Is TBN discussed? Is handedness mentioned? Improve if needed.",
        "checks": ["normal_matrix", "TBN", "handedness", "bitangent", "normal_map_sRGB", "mesh_tangents", "asset_pipeline", "shader_fix"],
    },

    # ── Engine: GPU Performance ──
    "engine_gpu_bottleneck_analysis": {
        "name": "GPU Performance — Bottleneck Diagnosis",
        "category": "game_engine",
        "engine_skill": "gpu_performance",
        "engine_skill_label": "Optimization",
        "difficulty": "hard",
        "text": "A game runs at 35 FPS on a mid-range GPU. CPU frame time is 8 ms, GPU frame time is 26 ms. Diagnose the bottleneck and propose a prioritized optimization plan.\n\nRequirements:\n- Explain CPU frame time vs GPU frame time.\n- Identify likely GPU bottleneck.\n- Discuss overdraw, shader complexity, shadow quality, post-processing and resolution.\n- Explain how to verify with GPU profiler or RenderDoc.\n- Provide concrete optimization steps.",
        "self_validation_hint": "Review bottleneck analysis. Is overdraw discussed? Is RenderDoc mentioned? Improve if needed.",
        "checks": ["CPU_frame_time", "GPU_frame_time", "GPU_bottleneck", "overdraw", "shader_complexity", "shadows", "post_processing", "RenderDoc", "optimization_plan"],
    },
    "engine_draw_call_optimization": {
        "name": "GPU Performance — Draw Calls, Batching and Instancing",
        "category": "game_engine",
        "engine_skill": "gpu_performance",
        "engine_skill_label": "Optimization",
        "difficulty": "hard",
        "text": "A scene has 20,000 small objects and the engine is CPU-bound due to draw calls. Propose and implement an optimization strategy.\n\nRequirements:\n- Explain draw call overhead.\n- Compare static batching, dynamic batching and GPU instancing.\n- Use frustum culling.\n- Use LODs.\n- Discuss material sorting.\n- Provide pseudo-code for batching or instancing.",
        "self_validation_hint": "Review optimization. Is frustum culling included? Are LODs discussed? Improve if needed.",
        "checks": ["draw_call", "CPU_bound", "static_batching", "dynamic_batching", "instancing", "frustum_culling", "LOD", "material_sorting"],
    },
    "engine_vram_texture_optimization": {
        "name": "GPU Performance — VRAM and Texture Optimization",
        "category": "game_engine",
        "engine_skill": "gpu_performance",
        "engine_skill_label": "Optimization",
        "difficulty": "hard",
        "text": "A game exceeds VRAM budget and stutters when entering new areas. Design a texture and asset memory optimization plan.\n\nRequirements:\n- Use texture compression.\n- Use mipmaps.\n- Use streaming.\n- Track memory budgets.\n- Discuss texture atlases and virtual texturing conceptually.\n- Explain how to avoid runtime stalls.\n- Provide practical debugging metrics.",
        "self_validation_hint": "Review VRAM optimization. Is streaming discussed? Are metrics included? Improve if needed.",
        "checks": ["VRAM", "texture_compression", "mipmaps", "streaming", "memory_budget", "texture_atlas", "virtual_texturing", "runtime_stalls", "metrics"],
    },

    # ── Engine: Unity ──
    "engine_unity_urp_render_feature": {
        "name": "Unity — URP Custom Render Feature",
        "category": "game_engine",
        "engine_skill": "unity",
        "engine_skill_label": "Unity",
        "difficulty": "hard",
        "text": "Write a Unity URP custom render feature that applies a simple full-screen post-processing effect.\n\nRequirements:\n- Create ScriptableRendererFeature.\n- Create ScriptableRenderPass.\n- Allocate and use temporary render targets correctly.\n- Blit source to destination with a material.\n- Expose settings in the inspector.\n- Explain where the pass is inserted in the render pipeline.",
        "self_validation_hint": "Review URP render feature. Is Blit used correctly? Is inspector exposure included? Improve if needed.",
        "checks": ["ScriptableRendererFeature", "ScriptableRenderPass", "temporary_render_target", "Blit", "Material", "Inspector", "RenderPassEvent"],
    },
    "engine_unity_job_system": {
        "name": "Unity — Job System and Burst",
        "category": "game_engine",
        "engine_skill": "unity",
        "engine_skill_label": "Unity",
        "difficulty": "hard",
        "text": "Convert a slow Unity MonoBehaviour loop that updates 100,000 agents into a Job System implementation.\n\nRequirements:\n- Use NativeArray.\n- Use IJobParallelFor or equivalent.\n- Avoid managed allocations inside jobs.\n- Explain Burst compatibility.\n- Schedule and complete the job safely.\n- Dispose native containers correctly.",
        "self_validation_hint": "Review Job System code. Are managed allocations avoided? Is Dispose called? Improve if needed.",
        "checks": ["NativeArray", "IJobParallelFor", "Burst", "Schedule", "Complete", "Dispose", "no_managed_allocation"],
    },
    "engine_unity_addressables_streaming": {
        "name": "Unity — Addressables and Scene Streaming",
        "category": "game_engine",
        "engine_skill": "unity",
        "engine_skill_label": "Unity",
        "difficulty": "hard",
        "text": "Design a Unity asset streaming system using Addressables for a large open-world game.\n\nRequirements:\n- Load and unload assets asynchronously.\n- Manage dependencies.\n- Avoid memory leaks.\n- Preload nearby areas.\n- Handle failed loads.\n- Explain how to profile memory usage.",
        "self_validation_hint": "Review Addressables design. Are memory leaks avoided? Is profiling explained? Improve if needed.",
        "checks": ["Addressables", "async_loading", "unload", "dependencies", "preload", "failed_loads", "memory_profile"],
    },

    # ── Engine: Unreal ──
    "engine_unreal_cpp_replication_actor": {
        "name": "Unreal — C++ Actor Replication",
        "category": "game_engine",
        "engine_skill": "unreal",
        "engine_skill_label": "Unreal",
        "difficulty": "hard",
        "text": "Write an Unreal Engine C++ Actor that replicates health and supports a server-authoritative damage function.\n\nRequirements:\n- Use replicated properties.\n- Implement GetLifetimeReplicatedProps.\n- Use server RPC correctly.\n- Explain authority checks.\n- Notify clients when health changes.\n- Include header and source snippets.",
        "self_validation_hint": "Review replication code. Is GetLifetimeReplicatedProps implemented? Are authority checks correct? Improve if needed.",
        "checks": ["AActor", "UPROPERTY", "Replicated", "GetLifetimeReplicatedProps", "Server_RPC", "Authority", "OnRep", "health"],
    },
    "engine_unreal_gas_ability": {
        "name": "Unreal — Gameplay Ability System",
        "category": "game_engine",
        "engine_skill": "unreal",
        "engine_skill_label": "Unreal",
        "difficulty": "hard",
        "text": "Design a simple Unreal Gameplay Ability System setup for a fireball ability.\n\nRequirements:\n- Define ability, input activation and cooldown.\n- Use gameplay effects for damage and cooldown.\n- Explain attributes.\n- Explain prediction and server authority.\n- Include C++/Blueprint integration notes.",
        "self_validation_hint": "Review GAS design. Is prediction explained? Are gameplay effects used? Improve if needed.",
        "checks": ["GameplayAbility", "GameplayEffect", "Attributes", "Cooldown", "Prediction", "ServerAuthority", "Blueprint", "Input"],
    },
    "engine_unreal_rdgraph_postprocess": {
        "name": "Unreal — Render Dependency Graph",
        "category": "game_engine",
        "engine_skill": "unreal",
        "engine_skill_label": "Unreal",
        "difficulty": "hard",
        "text": "Explain how to add a custom post-processing pass in Unreal Engine using Render Dependency Graph concepts.\n\nRequirements:\n- Explain RDG pass creation conceptually.\n- Explain input and output textures.\n- Explain shader parameters.\n- Discuss where the pass fits into the renderer.\n- Mention debugging and profiling.",
        "self_validation_hint": "Review RDG explanation. Are shader parameters discussed? Is profiling mentioned? Improve if needed.",
        "checks": ["RDG", "render_pass", "input_texture", "output_texture", "shader_parameters", "post_process", "profiling"],
    },

    # ── Engine: Godot ──
    "engine_godot_node_signal_system": {
        "name": "Godot — Nodes, Scenes and Signals",
        "category": "game_engine",
        "engine_skill": "godot",
        "engine_skill_label": "Godot",
        "difficulty": "hard",
        "text": "Create a Godot gameplay system using nodes, scenes and signals for a door that opens when the player collects a key.\n\nRequirements:\n- Use separate scenes for Player, Key and Door.\n- Use signals for communication.\n- Avoid hard-coded global references where possible.\n- Include GDScript code.\n- Explain the scene tree structure.",
        "self_validation_hint": "Review Godot code. Are signals used correctly? Is scene tree explained? Improve if needed.",
        "checks": ["Node", "Scene", "Signal", "GDScript", "Player", "Key", "Door", "scene_tree", "decoupling"],
    },
    "engine_godot_shader_water": {
        "name": "Godot — Water Shader",
        "category": "game_engine",
        "engine_skill": "godot",
        "engine_skill_label": "Godot",
        "difficulty": "hard",
        "text": "Write a Godot shader for stylized water.\n\nRequirements:\n- Animate UVs over time.\n- Add wave distortion.\n- Add fresnel-like edge highlight.\n- Support transparency.\n- Explain shader parameters for editor tweaking.",
        "self_validation_hint": "Review water shader. Is TIME used? Is transparency supported? Improve if needed.",
        "checks": ["shader_type", "TIME", "UV", "wave", "fresnel", "transparency", "uniform"],
    },
    "engine_godot_renderingdevice_compute": {
        "name": "Godot — RenderingDevice Compute",
        "category": "game_engine",
        "engine_skill": "godot",
        "engine_skill_label": "Godot",
        "difficulty": "hard",
        "text": "Explain how to use Godot RenderingDevice for a compute-style GPU task such as particle simulation.\n\nRequirements:\n- Explain buffers.\n- Explain shader dispatch.\n- Explain synchronization/readback considerations.\n- Describe how render data could use compute output.\n- Mention common limitations and debugging difficulties.",
        "self_validation_hint": "Review RenderingDevice usage. Is synchronization discussed? Are limitations mentioned? Improve if needed.",
        "checks": ["RenderingDevice", "buffer", "compute_shader", "dispatch", "synchronization", "readback", "particles", "debugging"],
    },

    # ── Engine: Physics ──
    "engine_physics_aabb_collision": {
        "name": "Physics — AABB Collision System",
        "category": "game_engine",
        "engine_skill": "physics",
        "engine_skill_label": "Physics",
        "difficulty": "hard",
        "text": "Implement a simple 2D AABB collision system in code.\n\nRequirements:\n- Define AABB data structure.\n- Detect overlap.\n- Resolve collision with minimum translation vector.\n- Separate dynamic and static objects.\n- Explain tunneling and how continuous collision detection helps.\n- Include test cases.",
        "self_validation_hint": "Review AABB system. Is MTV correct? Is tunneling discussed? Improve if needed.",
        "checks": ["AABB", "overlap", "MTV", "static", "dynamic", "tunneling", "CCD", "tests"],
    },
    "engine_physics_spatial_partitioning": {
        "name": "Physics — Broadphase Spatial Partitioning",
        "category": "game_engine",
        "engine_skill": "physics",
        "engine_skill_label": "Physics",
        "difficulty": "hard",
        "text": "Design a broadphase collision system for thousands of objects.\n\nRequirements:\n- Compare grid, quadtree, octree and BVH.\n- Pick one approach for a 2D top-down game.\n- Provide insertion/query pseudo-code.\n- Explain performance tradeoffs.\n- Explain when the structure should be rebuilt or updated incrementally.",
        "self_validation_hint": "Review spatial partitioning. Are tradeoffs explained? Is incremental update discussed? Improve if needed.",
        "checks": ["broadphase", "grid", "quadtree", "octree", "BVH", "query", "performance", "incremental_update"],
    },

    # ── Engine: Multiplayer ──
    "engine_multiplayer_prediction_reconciliation": {
        "name": "Multiplayer — Client Prediction and Server Reconciliation",
        "category": "game_engine",
        "engine_skill": "multiplayer",
        "engine_skill_label": "Multiplayer",
        "difficulty": "hard",
        "text": "Design a multiplayer movement system with client-side prediction and server reconciliation.\n\nRequirements:\n- Explain input sequence numbers.\n- Simulate movement locally.\n- Send inputs to the server.\n- Receive authoritative state.\n- Re-apply unacknowledged inputs.\n- Smooth corrections.\n- Explain common desync causes.",
        "self_validation_hint": "Review prediction system. Is reconciliation correct? Are desync causes explained? Improve if needed.",
        "checks": ["client_prediction", "server_reconciliation", "input_sequence", "authoritative_server", "replay_inputs", "smoothing", "desync"],
    },
    "engine_multiplayer_snapshot_interpolation": {
        "name": "Multiplayer — Snapshot Interpolation",
        "category": "game_engine",
        "engine_skill": "multiplayer",
        "engine_skill_label": "Multiplayer",
        "difficulty": "hard",
        "text": "Explain and implement snapshot interpolation for remote players in an online game.\n\nRequirements:\n- Buffer server snapshots.\n- Interpolate between snapshots with a delay.\n- Handle packet loss and jitter.\n- Explain tick rate vs render frame rate.\n- Provide pseudo-code.",
        "self_validation_hint": "Review snapshot interpolation. Is jitter handled? Is tick rate vs frame rate explained? Improve if needed.",
        "checks": ["snapshot", "interpolation", "buffer", "packet_loss", "jitter", "tick_rate", "render_frame_rate", "pseudo_code"],
    },

    # ── Engine: Asset Pipeline ──
    "engine_asset_gltf_importer": {
        "name": "Asset Pipeline — glTF Import",
        "category": "game_engine",
        "engine_skill": "asset_pipeline",
        "engine_skill_label": "Asset Pipeline",
        "difficulty": "hard",
        "text": "Design a glTF import pipeline for a custom engine.\n\nRequirements:\n- Load meshes, materials, textures, skeletons and animations.\n- Generate or validate tangents.\n- Convert materials to the engine format.\n- Create runtime-ready binary cache files.\n- Handle missing textures and invalid data.\n- Explain how hot reload should work.",
        "self_validation_hint": "Review glTF pipeline. Is hot reload explained? Are invalid data cases handled? Improve if needed.",
        "checks": ["glTF", "mesh", "material", "texture", "skeleton", "animation", "tangent", "binary_cache", "hot_reload", "invalid_data"],
    },
    "engine_asset_texture_compression": {
        "name": "Asset Pipeline — Texture Compression",
        "category": "game_engine",
        "engine_skill": "asset_pipeline",
        "engine_skill_label": "Asset Pipeline",
        "difficulty": "hard",
        "text": "Design a texture compression pipeline for PC and mobile builds.\n\nRequirements:\n- Choose formats for albedo, normal maps, masks and HDR textures.\n- Generate mipmaps.\n- Handle sRGB and linear textures correctly.\n- Explain platform-specific compression choices.\n- Include validation rules.",
        "self_validation_hint": "Review texture compression. Is sRGB vs linear handled? Are platform choices explained? Improve if needed.",
        "checks": ["texture_compression", "albedo", "normal_map", "mipmaps", "sRGB", "linear", "platform", "validation"],
    },

    # ── Engine: Editor Tools ──
    "engine_editor_level_validation_tool": {
        "name": "Editor Tools — Level Validation",
        "category": "game_engine",
        "engine_skill": "editor_tools",
        "engine_skill_label": "Editor Tools",
        "difficulty": "hard",
        "text": "Design an editor tool that scans a game level for common problems before shipping.\n\nRequirements:\n- Detect missing materials, missing collision, broken references and oversized textures.\n- Report severity levels.\n- Provide clickable links to objects if the engine supports it.\n- Allow automatic fixes for safe cases.\n- Export a JSON report.",
        "self_validation_hint": "Review validation tool. Are severity levels used? Is JSON export included? Improve if needed.",
        "checks": ["editor_tool", "missing_material", "missing_collision", "broken_reference", "oversized_texture", "severity", "auto_fix", "JSON_report"],
    },
    "engine_editor_debug_overlay": {
        "name": "Editor Tools — Runtime Debug Overlay",
        "category": "game_engine",
        "engine_skill": "editor_tools",
        "engine_skill_label": "Editor Tools",
        "difficulty": "hard",
        "text": "Design and implement a runtime debug overlay for a game engine.\n\nRequirements:\n- Show FPS, frame time, CPU time, GPU time and memory usage.\n- Show draw calls and triangle count if available.\n- Toggle visibility at runtime.\n- Keep overhead low.\n- Explain how data is collected.",
        "self_validation_hint": "Review debug overlay. Is overhead low? Is data collection explained? Improve if needed.",
        "checks": ["FPS", "frame_time", "CPU_time", "GPU_time", "memory", "draw_calls", "triangles", "toggle", "low_overhead"],
    },

    # ── Engine: Gameplay Systems ──
    "engine_gameplay_inventory_system": {
        "name": "Gameplay — Inventory System",
        "category": "game_engine",
        "engine_skill": "gameplay_systems",
        "engine_skill_label": "Gameplay",
        "difficulty": "hard",
        "text": "Design and implement an inventory system for an RPG.\n\nRequirements:\n- Support stackable and non-stackable items.\n- Support item metadata.\n- Support add, remove, move and split stack operations.\n- Prevent invalid states.\n- Serialize and deserialize inventory data.\n- Include edge cases.",
        "self_validation_hint": "Review inventory system. Are edge cases handled? Is serialization correct? Improve if needed.",
        "checks": ["inventory", "stackable", "metadata", "add", "remove", "split_stack", "serialization", "edge_cases"],
    },
    "engine_gameplay_save_load_system": {
        "name": "Gameplay — Save/Load System",
        "category": "game_engine",
        "engine_skill": "gameplay_systems",
        "engine_skill_label": "Gameplay",
        "difficulty": "hard",
        "text": "Design a robust save/load system for a game.\n\nRequirements:\n- Save player stats, inventory, quest state and world state.\n- Use versioned save data.\n- Handle missing or old fields.\n- Avoid corrupted saves by writing atomically.\n- Discuss encryption/compression optionally.\n- Include data schema example.",
        "self_validation_hint": "Review save/load system. Is versioning used? Is atomic write implemented? Improve if needed.",
        "checks": ["save_load", "versioning", "inventory", "quest_state", "world_state", "migration", "atomic_write", "schema"],
    },

    # ── Engine: 2D ──
    "engine_2d_tilemap_renderer": {
        "name": "2D Engine — Tilemap Renderer",
        "category": "game_engine",
        "engine_skill": "2d",
        "engine_skill_label": "2D Engine",
        "difficulty": "hard",
        "text": "Design a performant 2D tilemap renderer.\n\nRequirements:\n- Use chunks.\n- Batch tiles by texture/material.\n- Support camera culling.\n- Support animated tiles.\n- Support tile collision data.\n- Explain how to update only dirty chunks.",
        "self_validation_hint": "Review tilemap renderer. Are dirty chunks explained? Is batching used? Improve if needed.",
        "checks": ["tilemap", "chunks", "batching", "camera_culling", "animated_tiles", "collision", "dirty_chunks"],
    },
    "engine_2d_pixel_perfect_camera": {
        "name": "2D Engine — Pixel-Perfect Camera",
        "category": "game_engine",
        "engine_skill": "2d",
        "engine_skill_label": "2D Engine",
        "difficulty": "hard",
        "text": "Implement a pixel-perfect camera system for a 2D game.\n\nRequirements:\n- Preserve integer scaling.\n- Avoid subpixel jitter.\n- Support different screen resolutions.\n- Explain render texture approach.\n- Handle UI scaling separately.",
        "self_validation_hint": "Review pixel-perfect camera. Is integer scaling preserved? Is UI scaling separate? Improve if needed.",
        "checks": ["pixel_perfect", "integer_scaling", "subpixel_jitter", "resolution", "render_texture", "UI_scaling"],
    },

    # ── Engine: 3D ──
    "engine_3d_skeletal_animation": {
        "name": "3D Engine — Skeletal Animation System",
        "category": "game_engine",
        "engine_skill": "3d",
        "engine_skill_label": "3D Engine",
        "difficulty": "hard",
        "text": "Design a skeletal animation system for a 3D engine.\n\nRequirements:\n- Load skeleton hierarchy.\n- Store inverse bind pose matrices.\n- Interpolate keyframes.\n- Blend two animations.\n- Upload bone matrices to the GPU.\n- Explain CPU skinning vs GPU skinning.",
        "self_validation_hint": "Review skeletal animation. Is animation blending correct? Is GPU skinning explained? Improve if needed.",
        "checks": ["skeleton", "inverse_bind_pose", "keyframe_interpolation", "animation_blending", "bone_matrices", "GPU_skinning", "CPU_skinning"],
    },
    "engine_3d_lod_occlusion_streaming": {
        "name": "3D Engine — LOD, Occlusion and Scene Streaming",
        "category": "game_engine",
        "engine_skill": "3d",
        "engine_skill_label": "3D Engine",
        "difficulty": "hard",
        "text": "Design a large 3D world rendering system.\n\nRequirements:\n- Use LODs.\n- Use frustum culling.\n- Use occlusion culling.\n- Stream world chunks asynchronously.\n- Manage memory budget.\n- Avoid visible popping.\n- Explain debugging metrics.",
        "self_validation_hint": "Review 3D rendering system. Is occlusion culling used? Is popping avoided? Improve if needed.",
        "checks": ["LOD", "frustum_culling", "occlusion_culling", "streaming", "chunks", "memory_budget", "popping", "metrics"],
    },
}

ENGINE_QUICK_TEST_SET = [
    "engine_vulkan_triangle_swapchain",
    "engine_vulkan_texture_upload",
    "engine_glsl_pbr_fragment_shader",
    "engine_glsl_compute_particles",
    "engine_opengl_deferred_renderer",
    "engine_unity_urp_render_feature",
    "engine_unreal_cpp_replication_actor",
    "engine_godot_node_signal_system",
    "engine_gpu_bottleneck_analysis",
    "engine_draw_call_optimization",
]


def _load_songwriting_prompts_from_markdown() -> Dict[str, Dict[str, Any]]:
    """Load songwriting benchmark prompts from sogmaker.md."""
    path = os.path.join(os.path.dirname(__file__), "sogmaker.md")
    if not os.path.exists(path):
        logger.warning("Songwriting prompt file not found: %s", path)
        return {}

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    prompts: Dict[str, Dict[str, Any]] = {}
    sections = re.split(r"\n## `([^`]+)`\n", text)
    for i in range(1, len(sections), 2):
        key = sections[i].strip()
        body = sections[i + 1]
        prompt_match = re.search(r"```text\s*\n([\s\S]*?)\n```", body)
        checks_match = re.search(r"Checks:\s*```python\s*\n([\s\S]*?)\n```", body)
        if not prompt_match:
            continue

        def meta(label: str, default: str = "") -> str:
            match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", body)
            return match.group(1).strip() if match else default

        checks: List[str] = []
        if checks_match:
            try:
                parsed = ast.literal_eval(checks_match.group(1).strip())
                if isinstance(parsed, list):
                    checks = [str(item) for item in parsed]
            except (SyntaxError, ValueError):
                logger.warning("Could not parse checks for songwriting prompt %s", key)

        sub_category = meta("Kategorie", "Songwriting")
        language = meta("Sprache", "Unknown")
        genre = meta("Genre", "Songwriting")
        difficulty = meta("Schwierigkeit", "medium").lower()
        prompt_text = prompt_match.group(1).strip()

        prompts[key] = {
            "name": f"{sub_category} - {genre}",
            "category": "songwriting_tests",
            "sub_category": sub_category,
            "songwriting_skill": _songwriting_skill_from_metadata(key, sub_category, checks),
            "songwriting_skill_label": sub_category,
            "language": language,
            "genre": genre,
            "difficulty": difficulty,
            "text": prompt_text,
            "self_validation_hint": (
                "Review the lyrics against the task. Improve hook strength, rhyme, meter, "
                "emotion, structure and originality where relevant. "
                "Return only the final requested output, without explanations."
            ),
            "checks": checks,
        }
    return prompts


def _songwriting_skill_from_metadata(key: str, sub_category: str, checks: List[str]) -> str:
    value = " ".join([key, sub_category, *checks]).lower()
    if "rhyme" in value:
        return "rhyme"
    if "meter" in value or "singable" in value or "rhythm" in value:
        return "meter"
    if "emotion" in value or "regret" in value or "euphoria" in value:
        return "emotion"
    if "original" in value or "no_cliche" in value or "fresh" in value:
        return "originality"
    if "full_song" in value or "structure" in value or "story" in value:
        return "structure"
    return "hook"


def _songwriting_self_validation_hint() -> str:
    return (
        "Review the lyrics against the task. Improve hook strength, rhyme, meter, "
        "emotion, structure and originality where relevant. "
        "Return only the final requested output, without explanations."
    )


def _songwriting_language_prompt(
    *,
    sub_category: str,
    language: str,
    genre: str,
    difficulty: str,
    text: str,
    checks: List[str],
) -> Dict[str, Any]:
    return {
        "name": f"{sub_category} - {genre}",
        "category": "songwriting_tests",
        "sub_category": sub_category,
        "songwriting_skill": _songwriting_skill_from_metadata("", sub_category, checks),
        "songwriting_skill_label": sub_category,
        "language": language,
        "genre": genre,
        "difficulty": difficulty.lower(),
        "text": text.strip(),
        "self_validation_hint": _songwriting_self_validation_hint(),
        "checks": checks,
    }


def _songwriting_language_prompt_overrides() -> Dict[str, Dict[str, Any]]:
    """Canonical multilingual songwriting set shown in the UI."""
    return {
        "songwriting_language_english_indie_pop": _songwriting_language_prompt(
            sub_category="Language",
            language="English",
            genre="Indie Pop",
            difficulty="Easy",
            text="""
Write an English indie-pop chorus about someone who still feels close even after leaving.

Requirements:
- natural English
- simple words
- strong hook
- 4 to 6 lines
- intimate, modern indie-pop feel
- no explanations
""",
            checks=["english", "natural_language", "indie_pop", "hook", "chorus", "singable"],
        ),
        "songwriting_language_spanish_reggaeton": _songwriting_language_prompt(
            sub_category="Language",
            language="Spanish",
            genre="Reggaeton Pop",
            difficulty="Medium",
            text="""
Escribe un coro de reggaeton pop sobre una última noche bailando con alguien que todavía amas.

Requisitos:
- solo letra en español
- lenguaje natural
- hook repetible
- líneas cortas
- romántico pero no explícito
- sin explicación
""",
            checks=["spanish", "natural_language", "reggaeton", "hook", "short_lines", "safe_content"],
        ),
        "songwriting_language_french_chanson_pop": _songwriting_language_prompt(
            sub_category="Language",
            language="French",
            genre="Chanson Pop",
            difficulty="Medium",
            text="""
Écris un refrain chanson-pop français sur le regret d'avoir laissé partir quelqu'un.

Exigences:
- paroles en français uniquement
- langage naturel
- 4 à 6 lignes
- refrain mémorable
- émotion élégante, pas mélodramatique
- pas d'explication
""",
            checks=["french", "natural_language", "chanson_pop", "chorus", "hook", "regret"],
        ),
        "songwriting_language_italian_italo_disco": _songwriting_language_prompt(
            sub_category="Language",
            language="Italian",
            genre="Italo Disco",
            difficulty="Medium",
            text="""
Scrivi un ritornello italo disco in italiano su due persone che si ritrovano sotto le luci della città.

Requisiti:
- solo testo in italiano
- linguaggio naturale
- 4 a 6 versi
- hook forte e cantabile
- energia notturna anni 80 moderna
- nessuna spiegazione
""",
            checks=["italian", "natural_language", "italo_disco", "hook", "chorus", "singable"],
        ),
        "songwriting_language_dutch_nederpop": _songwriting_language_prompt(
            sub_category="Language",
            language="Dutch",
            genre="Nederpop",
            difficulty="Medium",
            text="""
Schrijf een Nederlands nederpop-refrein over iemand die een verloren liefde niet kan vergeten.

Vereisten:
- alleen Nederlandse songtekst
- natuurlijke taal
- 4 tot 6 regels
- sterke hook
- nuchter maar emotioneel
- geen uitleg
""",
            checks=["dutch", "natural_language", "nederpop", "hook", "chorus", "short_lines"],
        ),
        "songwriting_language_polish_synth_pop": _songwriting_language_prompt(
            sub_category="Language",
            language="Polish",
            genre="Synth Pop",
            difficulty="Medium",
            text="""
Napisz polski refren synth-pop o kimś, kto wciąż czeka na wiadomość od dawnej miłości.

Wymagania:
- tylko tekst po polsku
- naturalny język
- 4 do 6 wersów
- mocny hook
- melancholijny, nocny klimat syntezatorów
- bez wyjaśnień
""",
            checks=["polish", "natural_language", "synth_pop", "hook", "chorus", "simple_emotion"],
        ),
        "songwriting_language_turkish_arabesque_pop": _songwriting_language_prompt(
            sub_category="Language",
            language="Turkish",
            genre="Arabesque Pop",
            difficulty="Medium",
            text="""
Eski bir aşkı unutamayan biri hakkında Türkçe arabesk pop nakaratı yaz.

Gereksinimler:
- sadece Türkçe şarkı sözü
- doğal günlük dil
- 4 ila 6 kısa satır
- güçlü hook
- duygulu ama modern
- açıklama yok
""",
            checks=["turkish", "natural_language", "arabesque_pop", "hook", "chorus", "short_lines"],
        ),
        "songwriting_language_greek_laiko_pop": _songwriting_language_prompt(
            sub_category="Language",
            language="Greek",
            genre="Laiko Pop",
            difficulty="Hard",
            text="""
Γράψε ένα ελληνικό laiko-pop ρεφρέν για κάποιον που έχασε την ευκαιρία να πει όσα ένιωθε.

Απαιτήσεις:
- μόνο ελληνικοί στίχοι
- φυσική καθημερινή γλώσσα
- καθαρό hook
- 4 έως 6 γραμμές
- συναίσθημα που τραγουδιέται
- χωρίς εξηγήσεις
""",
            checks=["greek", "natural_language", "laiko_pop", "hook", "chorus", "singable"],
        ),
        "songwriting_language_korean_kpop": _songwriting_language_prompt(
            sub_category="Language",
            language="Korean/English",
            genre="K-Pop",
            difficulty="Hard",
            text="""
Write a K-pop chorus using mostly Korean with one short English hook phrase.

Theme:
Coming back stronger after heartbreak.

Requirements:
- mostly Korean lyrics
- one repeatable English hook phrase
- catchy pop rhythm
- confident emotion
- no translation
- no explanations
""",
            checks=["korean", "english_hook", "kpop", "confidence", "chorus", "no_translation"],
        ),
    }


def _active_songwriting_prompts() -> Dict[str, Dict[str, Any]]:
    prompts = _load_songwriting_prompts_from_markdown()
    for key in (
        "songwriting_language_german_pop",
        "songwriting_language_english_pop",
        "songwriting_language_greek_pop",
        "songwriting_language_french_pop",
        "songwriting_language_polish_pop",
        "songwriting_language_turkish_pop",
        "songwriting_language_albanian_pop",
        "songwriting_language_dutch_pop",
    ):
        prompts.pop(key, None)

    prompts = {
        key: prompt
        for key, prompt in prompts.items()
        if "suno" not in " ".join([
            key,
            str(prompt.get("name", "")),
            str(prompt.get("sub_category", "")),
            str(prompt.get("songwriting_skill", "")),
            str(prompt.get("genre", "")),
            " ".join(str(check) for check in prompt.get("checks", [])),
        ]).lower()
    }
    prompts.update(_songwriting_language_prompt_overrides())
    return prompts


PROMPTS.update(_active_songwriting_prompts())


def _send_prompt(server_url: str, model_name: str, prompt_text: str,
                 context_size: int, max_tokens: int,
                 temperature: float, top_p: float,
                 on_token: Optional[Callable[[str, str], None]] = None) -> Optional[Dict[str, Any]]:
    result = send_completion(
        server_url=server_url,
        prompt=prompt_text,
        model_name=model_name,
        context_size=context_size,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        on_token=on_token,
    )
    if result is None:
        logger.info("Fallback: Trying /v1/chat/completions")
        messages = [{"role": "user", "content": prompt_text}]
        result = send_chat_completion(
            server_url=server_url,
            messages=messages,
            model_name=model_name,
            context_size=context_size,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            on_token=on_token,
        )
    return result


def run_single_prompt(server_url: str, model_name: str, prompt_key: str,
                      context_size: int = 4096, max_tokens: int = 512,
                      temperature: float = 0.7, top_p: float = 0.9,
                      enable_self_validation: bool = True,
                      on_token: Optional[Callable[[str, str], None]] = None) -> Optional[Dict[str, Any]]:
    prompt = PROMPTS.get(prompt_key)
    if not prompt:
        logger.error("Unknown prompt key: %s", prompt_key)
        return None

    logger.info("Starting prompt '%s' for model '%s'", prompt["name"], model_name)
    metrics = get_system_metrics()

    if on_token:
        on_token("status", f"── Run 1: {prompt['name']} ──")

    # ── Run 1: Blind prompt ──
    run1_result = _send_prompt(server_url, model_name, prompt["text"],
                               context_size, max_tokens, temperature, top_p,
                               on_token=on_token)
    if run1_result is None:
        logger.error("Run 1 failed for prompt '%s'", prompt["name"])
        # Return failed result instead of None
        return {
            "model_name": model_name,
            "server_url": server_url,
            "context_size": context_size,
            "prompt_name": prompt["name"],
            "prompt_text": prompt.get("text"),
            "prompt_key": prompt_key,
            "prompt_category": prompt.get("category", "general"),
            "programming_language": prompt.get("language") if prompt.get("category") == "coding_language" else None,
            "programming_language_label": prompt.get("language_label"),
            "engine_skill": prompt.get("engine_skill"),
            "engine_skill_label": prompt.get("engine_skill_label"),
            "songwriting_skill": prompt.get("songwriting_skill"),
            "songwriting_skill_label": prompt.get("songwriting_skill_label"),
            "status": "failed",
            "error_message": "Run 1 failed - server unreachable or timeout",
            "generation_tokens_per_second": 0,
            "prompt_tokens_per_second": 0,
            "total_tokens": 0,
            "total_duration": 0,
            "first_token_latency": 0,
            "avg_token_latency": 0,
            "ram_usage_mb": metrics.get("ram_usage_mb"),
            "vram_usage_mb": metrics.get("vram_usage_mb"),
            "quality_score": 0,
            "format_score": 0,
            "consistency_score": 50.0,
            "context_score": calculate_context_score(context_size),
            "stability_score": 0,
            "final_score": 0,
        }

    run1_content = run1_result.get("content", "")

    # ── Run 2: Self-validation ──
    run2_content = ""
    run2_result = None
    if enable_self_validation:
        validation_prompt = (
            f"Here is your previous answer to a task:\n\n"
            f"--- BEGIN PREVIOUS ANSWER ---\n{run1_content}\n--- END PREVIOUS ANSWER ---\n\n"
            f"Task: {prompt['text']}\n\n"
            f"{prompt['self_validation_hint']}\n\n"
            f"Provide your improved final answer below."
        )
        if on_token:
            on_token("status", "── Run 2: Self-Validation ──")
        run2_result = _send_prompt(server_url, model_name, validation_prompt,
                                   context_size, max_tokens, temperature, top_p,
                                   on_token=on_token)
        if run2_result:
            run2_content = run2_result.get("content", "")
        else:
            # Run 2 also failed
            run2_content = run1_content  # Use Run 1 as fallback
            run2_result = run1_result  # Use Run 1 as fallback

    # ── Use best result (Run 2 if available, else Run 1) ──
    best_result = run2_result if run2_result else run1_result
    best_content = run2_content if run2_content else run1_content

    # ── Scoring ──
    quality = evaluate_response_quality(best_content, prompt["name"])
    fmt = validate_format(best_content, prompt["name"])
    consistency = calculate_consistency_score(run1_content, run2_content) if run2_content else {"total": 50.0}
    context = calculate_context_score(context_size)

    run1_quality = evaluate_response_quality(run1_content, prompt["name"])
    run2_quality = evaluate_response_quality(run2_content, prompt["name"]) if run2_content else {"total": 0}

    final_score = calculate_final_score(
        generation_tokens_per_second=best_result.get("generation_tokens_per_second", 0),
        prompt_tokens_per_second=best_result.get("prompt_tokens_per_second", 0),
        quality_score=quality["total"],
        stability_score=100,
        context_score=context,
        format_score=fmt["format_score"],
        consistency_score=consistency["total"],
        first_token_latency=best_result.get("first_token_latency", 0) or 0,
    )

    # Language-specific fields for coding-language prompts
    prompt_checks = prompt.get("checks", [])
    prompt_category = prompt.get("category", "general")
    prompt_language = prompt.get("language") if prompt_category == "coding_language" else None
    prompt_language_label = prompt.get("language_label") if prompt_category == "coding_language" else None

    language_info = {}
    if prompt_language:
        language_info = calculate_language_score(
            content=best_content,
            language=prompt_language,
            checks=prompt_checks,
            quality_score=quality["total"],
            format_score=fmt["format_score"],
        )

    # Engine-specific fields for game-engine prompts
    prompt_engine_skill = prompt.get("engine_skill")
    prompt_engine_skill_label = prompt.get("engine_skill_label")

    engine_info = {}
    if prompt_engine_skill:
        engine_info = calculate_engine_score(
            content=best_content,
            engine_skill=prompt_engine_skill,
            checks=prompt_checks,
            quality_score=quality["total"],
            format_score=fmt["format_score"],
        )

    # Songwriting-specific fields for songwriting tests
    prompt_songwriting_skill = prompt.get("songwriting_skill")
    prompt_songwriting_skill_label = prompt.get("songwriting_skill_label")

    songwriting_info = {}
    if prompt_category == "songwriting_tests":
        songwriting_info = calculate_songwriting_scores(
            content=best_content,
            checks=prompt_checks,
            quality_score=quality["total"],
            format_score=fmt["format_score"],
        )

    return {
        "model_name": model_name,
        "server_url": server_url,
        "context_size": context_size,
        "prompt_name": prompt["name"],
        "prompt_text": prompt["text"],
        "prompt_key": prompt_key,
        "prompt_category": prompt_category,
        "programming_language": prompt_language,
        "programming_language_label": prompt_language_label,
        "engine_skill": prompt_engine_skill,
        "engine_skill_label": prompt_engine_skill_label,
        "songwriting_skill": prompt_songwriting_skill,
        "songwriting_skill_label": prompt_songwriting_skill_label,
        "prompt_tokens": best_result.get("prompt_tokens", 0),
        "completion_tokens": best_result.get("completion_tokens", 0),
        "total_tokens": best_result.get("total_tokens", 0),
        "prompt_tokens_per_second": best_result.get("prompt_tokens_per_second", 0),
        "generation_tokens_per_second": best_result.get("generation_tokens_per_second", 0),
        "total_duration": best_result.get("total_duration", 0),
        "first_token_latency": best_result.get("first_token_latency"),
        "avg_token_latency": best_result.get("avg_token_latency", 0),
        "ram_usage_mb": metrics.get("ram_usage_mb"),
        "vram_usage_mb": metrics.get("vram_usage_mb"),
        "quality_score": quality["total"],
        "quality_details": quality,
        "format_score": fmt["format_score"],
        "format_checks": fmt["checks"],
        "consistency_score": consistency["total"],
        "consistency_details": consistency,
        "context_score": context,
        "stability_score": 100,
        "final_score": final_score,
        "language_score": language_info.get("score", 0),
        "language_rating": language_info.get("rating"),
        "language_rating_label": language_info.get("label"),
        "engine_score": engine_info.get("score", 0),
        "engine_rating": engine_info.get("rating"),
        "engine_rating_label": engine_info.get("label"),
        "songwriting_score": songwriting_info.get("score", 0),
        "songwriting_rating": songwriting_info.get("rating"),
        "songwriting_rating_label": songwriting_info.get("label"),
        "songwriting_hook_score": songwriting_info.get("hook_score", 0),
        "songwriting_rhyme_score": songwriting_info.get("rhyme_score", 0),
        "songwriting_meter_score": songwriting_info.get("meter_score", 0),
        "songwriting_emotion_score": songwriting_info.get("emotion_score", 0),
        "songwriting_structure_score": songwriting_info.get("structure_score", 0),
        "songwriting_originality_score": songwriting_info.get("originality_score", 0),
        "run1_content": run1_content,
        "run1_quality_score": run1_quality["total"],
        "run1_tokens_per_second": run1_result.get("generation_tokens_per_second", 0),
        "run2_content": run2_content,
        "run2_quality_score": run2_quality["total"],
        "run2_tokens_per_second": run2_result.get("generation_tokens_per_second", 0) if run2_result else 0,
        "self_validation_used": enable_self_validation and run2_result is not None,
        "status": "finished",
        "error_message": None,
    }


def run_benchmark(model_name: str, server_url: str, prompt_keys: List[str],
                  context_size: int = 4096, max_tokens: int = 512,
                  temperature: float = 0.7, top_p: float = 0.9,
                  num_runs: int = 1,
                  enable_self_validation: bool = True,
                  on_progress: Optional[Callable[[int, str, float, int], None]] = None,
                  abort_flag: Optional[Callable[[], bool]] = None,
                  on_token: Optional[Callable[[str, str], None]] = None) -> List[Dict[str, Any]]:
    all_results = []

    if not check_health(server_url):
        logger.error("llama-server at %s not reachable!", server_url)
        return []

    total_steps = len(prompt_keys) * num_runs
    current_step = 0

    for run_num in range(num_runs):
        for prompt_key in prompt_keys:
            if abort_flag and abort_flag():
                logger.info("Benchmark aborted at step %d/%d", current_step, total_steps)
                return []

            current_step += 1
            progress = int((current_step / total_steps) * 100)
            pass_label = " (Run 1 + Self-Validation)" if enable_self_validation else ""
            step_desc = f"Prompt {current_step}/{total_steps}: {PROMPTS.get(prompt_key, {}).get('name', prompt_key)}{pass_label}"

            logger.info("Benchmark step %d/%d (%d%%)", current_step, total_steps, progress)

            if on_progress:
                on_progress(progress, step_desc, 0, 0)

            result = run_single_prompt(
                server_url=server_url,
                model_name=model_name,
                prompt_key=prompt_key,
                context_size=context_size,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                enable_self_validation=enable_self_validation,
                on_token=on_token,
            )

            if result:
                result["run_number"] = run_num + 1
                all_results.append(result)
                if on_progress:
                    on_progress(
                        progress,
                        step_desc,
                        result.get("generation_tokens_per_second", 0),
                        result.get("completion_tokens", 0),
                    )

    return all_results


def _average_results(results: List[Dict[str, Any]], error_count: int = 0, total_runs: int = 0) -> Dict[str, Any]:
    if not results:
        return {}

    n = len(results)
    
    # Count errors from results (number of failed runs)
    error_count = sum(1 for r in results if r.get("status") == "failed")
    
    stability = calculate_stability_from_runs(results, error_count, n)

    avg_quality = sum(r.get("quality_score", 50) for r in results) / n
    avg_format = sum(r.get("format_score", 50) for r in results) / n
    avg_consistency = sum(r.get("consistency_score", 50) for r in results) / n
    avg_context = results[0].get("context_score", 50)

    avg_gen_tps = sum(r["generation_tokens_per_second"] for r in results) / n
    avg_prompt_tps = sum(r["prompt_tokens_per_second"] for r in results) / n
    avg_first_latency = sum(r["first_token_latency"] or 0 for r in results) / n

    final_score = calculate_final_score(
        generation_tokens_per_second=avg_gen_tps,
        prompt_tokens_per_second=avg_prompt_tps,
        quality_score=avg_quality,
        stability_score=stability,
        context_score=avg_context,
        format_score=avg_format,
        consistency_score=avg_consistency,
        first_token_latency=avg_first_latency,
    )

    avg = {
        "model_name": results[0]["model_name"],
        "server_url": results[0]["server_url"],
        "context_size": results[0]["context_size"],
        "prompt_name": f"Average ({n} prompts)",
        "prompt_text": "",
        "prompt_tokens": round(sum(r["prompt_tokens"] for r in results) / n),
        "completion_tokens": round(sum(r["completion_tokens"] for r in results) / n),
        "total_tokens": round(sum(r["total_tokens"] for r in results) / n),
        "prompt_tokens_per_second": round(avg_prompt_tps, 2),
        "generation_tokens_per_second": round(avg_gen_tps, 2),
        "total_duration": round(sum(r["total_duration"] for r in results) / n, 2),
        "first_token_latency": round(avg_first_latency, 2),
        "avg_token_latency": round(sum(r["avg_token_latency"] for r in results) / n, 4),
        "ram_usage_mb": results[0].get("ram_usage_mb"),
        "vram_usage_mb": results[0].get("vram_usage_mb"),
        "quality_score": round(avg_quality, 2),
        "format_score": round(avg_format, 2),
        "consistency_score": round(avg_consistency, 2),
        "context_score": avg_context,
        "stability_score": stability,
        "final_score": final_score,
        "self_validation_used": any(r.get("self_validation_used", False) for r in results),
        "status": "finished",
        "error_message": None,
    }
    return avg
