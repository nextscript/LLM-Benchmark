# Test Prompts

## General Tests

| Prompt Key | Name | Purpose |
|---|---|---|
| `coding` | Coding Test | Write a clean Python function that reads a large log file, detects errors, and returns a summary |
| `reasoning` | Reasoning Test | Mathematical/logical task: calculate parallel workers needed |
| `long_context` | Long Context Test | Summarize long texts and identify errors, risks, and improvements |
| `german_text` | German Text Test | Write a technical explanation in German |
| `json_test` | JSON Test | Create a valid JSON configuration for a local Llama server |

---

## Coding Language Tests

### Python

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_python_sales_analysis` | Data Processing | `def, type_hints, dict, invalid_rows, sorting, complexity` |
| `coding_python_async_api_client` | Async API Client | `asyncio, aiohttp, retry, timeout, http_errors, separate_results` |
| `coding_python_cli_largest_files` | CLI Tool | `argparse, recursive, permission_errors, sorting, pathlib, main_guard` |

### JavaScript

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_javascript_group_orders` | Array/Object Logic | `function, reduce, grouping, filter_cancelled, sorting, example` |
| `coding_javascript_cached_fetch` | Async Fetch Cache | `fetch, cache, promise_dedup, error_handling, async, modern_js` |
| `coding_javascript_searchable_list` | DOM Component | `dom, input_event, filter, highlight, no_library, render` |

### TypeScript

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_typescript_invoice` | Strong Typing | `interface, types, validation, totals, no_any, example` |
| `coding_typescript_api_response_validation` | API Response Validation | `generic, type_guard, narrowing, no_any, ApiResponse, example` |
| `coding_typescript_state_manager` | State Manager | `generic, subscribe, unsubscribe, state_change, types, example` |

### Java

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_java_user_service` | Service Class | `class, Optional, encapsulation, duplicate_check, Map, main` |
| `coding_java_worker_executor` | Multithreading | `ExecutorService, Callable_or_Runnable, shutdown, exceptions, thread_safe_counts, main` |
| `coding_java_csv_inventory` | File Parser | `csv, try_with_resources, validation, BigDecimal_or_double, class, total` |

### C#

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_csharp_linq_orders` | LINQ Data Processing | `LINQ, GroupBy, Where, OrderByDescending, Take, models` |
| `coding_csharp_async_http_downloader` | Async HTTP Client | `HttpClient, async, await, timeout, error_handling, no_blocking` |
| `coding_csharp_repository_pattern` | Repository Pattern | `interface, generic, repository, CRUD, missing_items, example` |

### C++

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_cpp_transactions` | Modern C++ Data Processing | `C++17, struct, std::vector, std::unordered_map, invalid, main` |
| `coding_cpp_raii_resource_manager` | Memory Safety | `RAII, unique_ptr_or_shared_ptr, destructor, no_raw_owning_pointer, class, memory_safe` |
| `coding_cpp_longest_unique_substring` | Algorithm Task | `sliding_window, unordered_map_or_set, pair_or_struct, tests, complexity, edge_cases` |

### C

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_c_integer_parser` | String Parser | `malloc, free, strtol, bounds, invalid_tokens, main` |
| `coding_c_file_statistics` | File Statistics | `fopen, fgetc_or_fread, exit_codes, large_file, error_handling, no_gets` |
| `coding_c_hash_table` | Simple Hash Table | `struct, hash, collision, insert, delete, free` |

### Go

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_go_worker_pool` | Concurrent Worker Pool | `goroutine, channel, worker_pool, WaitGroup, errors, no_leak` |
| `coding_go_http_task_server` | HTTP API Server | `net/http, json, handlers, status_codes, validation, stdlib` |
| `coding_go_log_parser` | Log Parser | `regexp_or_strings, struct, map, malformed, tests, status_count` |

### Rust

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_rust_word_frequency` | Ownership and Error Handling | `Result, HashMap, BufRead, ownership, sort, error_handling` |
| `coding_rust_cli_line_filter` | CLI Parser | `env_args, Result, BufReader, enumerate, no_panic, main` |
| `coding_rust_shape_trait` | Struct and Traits | `trait, struct, impl, Box<dyn, Vec, methods` |

### PHP

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_php_form_validation` | Form Validation | `filter_var, password_hash, errors, sanitize, strict_types, example` |
| `coding_php_router` | Simple Router | `class, GET, POST, dynamic_params, 404, no_dependency` |
| `coding_php_pdo_database` | Database Layer | `PDO, prepare, execute, try_catch, findById, sql_injection_safe` |

### Ruby

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_ruby_expense_grouping` | Data Transformation | `def, hash, grouping, validation, sort_by, example` |
| `coding_ruby_file_renamer` | CLI Script | `ARGV, File, rename, exist_check, errors, summary` |
| `coding_ruby_todo_list` | Class Design | `class, initialize, methods, validation, status, example` |

### Kotlin

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_kotlin_product_manager` | Data Classes | `data class, filter, sumOf, sortedBy, nullable_safe, main` |
| `coding_kotlin_coroutines_loader` | Coroutines | `suspend, coroutineScope, async, awaitAll, Result, no_blocking` |
| `coding_kotlin_null_safe_profile` | Null Safety | `nullable, ?, no_double_bang, data class, tests, display_name` |

### Swift

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_swift_book_filter` | Model and Filtering | `struct, filter, sorted, map, example, types` |
| `coding_swift_async_json_fetch` | Async/Await | `async, await, Codable, URLSession, do_catch, typed_result` |
| `coding_swift_payable_protocol` | Protocols | `protocol, struct_or_class, implementation, array, reduce, example` |

### Dart

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_dart_task_processing` | List Processing | `class, List, where, sort, DateTime, summary` |
| `coding_dart_async_resource_loader` | Async Future Handling | `Future, async, await, try_catch, separate_results, no_blocking` |
| `coding_dart_flutter_task_card` | Flutter Widget | `Widget, StatelessWidget, build, Text, Container_or_Card, no_package` |

### SQL

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_sql_sales_query` | Sales Query | `SELECT, JOIN, SUM, GROUP BY, WHERE, ORDER BY` |
| `coding_sql_duplicate_users` | Duplicate Detection | `SELECT, COUNT, GROUP BY, HAVING, MIN, MAX` |
| `coding_sql_monthly_report` | Monthly Report | `date_grouping, SUM, COUNT, LEFT JOIN_or_series, completed, explanation` |

### Bash

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_bash_backup_script` | Backup Script | `set -euo pipefail, tar, timestamp, validation, find, quoting` |
| `coding_bash_log_scanner` | Log Scanner | `find, grep, sort, head, quoting, strict_mode` |
| `coding_bash_process_monitor` | Process Monitor | `pgrep, restart, logging, args, validation, exit_codes` |

### PowerShell

| Prompt Key | Task | Main Checks |
|---|---|---|
| `coding_powershell_system_report` | System Report | `Get-CimInstance, Get-PSDrive, ConvertTo-Json, try_catch, parameters, output` |
| `coding_powershell_file_cleanup` | File Cleanup | `param, Get-ChildItem, Where-Object, WhatIf_or_DryRun, Remove-Item, summary` |
| `coding_powershell_service_checker` | Service Checker | `Get-Service, Restart-Service, param, logging, missing_service, switch` |

---

## Rating System

Language scores are calculated based on:

- **Quality Score** (45%): Response structure, completeness, relevance, technical accuracy
- **Format Score** (25%): Code formatting, syntax correctness
- **Language Syntax Score** (20%): Idiomatic use of language-specific features
- **Required Checks** (10%): Presence of expected keywords/patterns

### Score Thresholds

| Score | Rating | Label | Badge |
|-------|--------|-------|-------|
| ≥ 75 | `good` | Kann gut | 🟢 Green |
| ≥ 45 | `medium` | Kann mittel | 🟠 Orange |
| < 45 | `bad` | Kann schlecht | 🔴 Red |

> **Note**: This evaluation is heuristic-based. It does not mean the code actually compiles or passes tests. For real verification, a sandbox runner per language would be needed.
