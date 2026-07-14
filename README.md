<img src="https://raw.githubusercontent.com/nextscript/LLM-Benchmark/refs/heads/main/screen.PNG">

# LLM Benchmark WebGUI

A local web GUI for testing, comparing, and ranking `llama.cpp` / `llama-server` models.

Benchmark various models, store all measurements, and get an automatic ranking - find the best model for your hardware and use case.

---

## Features

- **Multi-Pass Evaluation**: Run 1 (blind) + Run 2 (self-validation) for deeper insights
- **Traceable Scoring**: Quality, Format, Consistency, Performance, Stability, Context
- **Multi-Language Coding Benchmarks**: Python, JavaScript, TypeScript, Java, C#, C++, C, Go, Rust, PHP, Ruby, Kotlin, Swift, Dart, SQL, Bash, PowerShell (51 language-specific prompts + 5 general prompts)
- **Game Engine & Graphics Programming Benchmarks**: Vulkan, GLSL, HLSL, OpenGL, DirectX 12, WebGPU, Unity, Unreal, Godot, Rendering, Shader, Physics, Multiplayer, Optimization, Asset Pipeline, Editor Tools, 2D/3D Engine (30+ engine-specific prompts)
- **Songwriting Benchmarks**: 52 prompts loaded from `sogmaker.md` for hooks, rhymes, meter, emotion, structure, originality, and Suno/AI-music formatting
- **Truth-Audit Benchmarks**: Dedicated prompts for claim checking, contradiction detection, and hallucination resistance
- **General Test Badges**: Icon badges for Coding, Reasoning, Long Context, German Text, and JSON tests
- **Programming Language Badges**: Green/orange/red badges with Devicon logos show whether a model is good, medium, or weak for each language
- **Engine Skill Badges**: Green/orange/red badges show proficiency in game engine and graphics programming domains
- **Songwriting Badges**: Green/orange/red badge row shows separate songwriting ability for Hook, Rhyme, Meter, Emotion, Structure, Originality, and Suno Format
- **Comparison Dashboard**: Canvas charts for badge scores by model, Blind Analysis vs. Self-Validation, run history, and separate Truth-Audit scores
- **Configurable Benchmark Parameters**: max tokens, temperature, top-p, self-validation toggle; decimal values accept dot or comma notation (`0.95` or `0,95`)
- **Run History**: Re-running the same model/category/prompt stores a new historical result, while Results and Ranking use the latest result per prompt
- **Benchmark Abort**: Cancel running benchmarks at any time
- **Benchmark Start**: Configure model, server URL, context size, and prompts
- **Live Status**: Track the benchmark in real-time with animation and progress bar
- **Total Elapsed Per Result**: The wall-clock time of each benchmark run is calculated from the run's start/finish timestamps and stored as `elapsed_seconds` (also available in the API and in the database) - basis for the Fastest Model (Elapsed) cards on the Dashboard and the Comparisons page
- **Results Elapsed Column**: Each row shows the overall benchmark elapsed time (e.g. `MM:SS` or `H:MM:SS`) - allows sorting to quickly find the fastest model
- **Ranking Elapsed Column**: The ranking table also shows total elapsed time per model, so the fastest model by wall-clock time is clearly visible
- **Automatic Ranking**: Score calculation based on multiple dimensions
- **SQLite Storage**: All results persist after restart
- **Dark Theme**: Modern, eye-friendly design
- **Completion Alert**: Sound + modal after benchmark completion
- **Dashboard**: Clear statistics cards including Fastest Model (Elapsed)
- **Start Scripts**: One-click launch via `start.bat` (Windows) or `start.sh` (Linux/macOS)

---

## Installation

### Quick Start (Windows)

```bash
start.bat
```

### Quick Start (Linux/macOS)

```bash
chmod +x start.sh
./start.sh
```

### Manual Installation

```bash
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `jinja2` | Template engine |
| `requests` | HTTP client for llama-server |
| `pydantic` | Data validation |
| `python-multipart` | File upload support |
| `psutil` | System metrics (RAM/VRAM) |

---

## Getting Started

### 1. Start llama-server

```bash
llama-server -m models/your-model.gguf -c 4096 --host 127.0.0.1 --port 8080 --metrics --slots
```

`--metrics` exposes the precise live tokens/s metric used by the benchmark status. Without it, the app falls back to `/slots` counters when available.

### 2. Start Benchmark App

```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```

### 3. Open WebGUI

Open browser at **http://localhost:5000**.

---

## Usage

### Start Benchmark

1. Open the **Benchmark** page
2. Enter model name and server URL
3. Configure context size, number of runs, max tokens, temperature, and top-p
4. Select prompts from grouped categories (General Tests, Coding Languages, Game Engine, Songwriting Tests, Truth-Audit)
5. Toggle self-validation on/off
6. Click **"Start Benchmark"**
7. Follow the live status with animation
8. After completion: sound + modal appear

Temperature and Top-P accept both decimal formats, for example `0.95` and `0,95`.

### Abort Benchmark

Click the **Abort** button during a running benchmark to cancel it.

### View Ranking

The **Ranking** page shows all tested models sorted by:

1. Highest total score
2. Highest Generation Tokens/s
3. Lowest First Token Latency
4. Highest stability

Each model displays:
- Total **Elapsed** time per result (wall-clock time of the run) for quickly finding the fastest model
- Color-coded **general test badges** for Coding, Reasoning, Long Context, German Text, and JSON
- Color-coded **programming language badges** showing coding proficiency per language
- Color-coded **engine skill badges** showing game engine and graphics programming proficiency
- Color-coded **songwriting badges** showing separate ability for Hook, Rhyme, Meter, Emotion, Structure, Originality, and Suno Format

Results and ranking are grouped by model name. If the same model is tested repeatedly, historical rows are preserved for comparison, while the visible aggregate uses the newest result for each prompt.

### View Results

The **Results** table shows all measured values:

- Prompt/Generation Tokens
- Tokens per second
- Elapsed (total benchmark wall-clock time)
- First Token Latency
- Average Token Latency
- General test badges with proficiency rating
- Language badge with proficiency rating
- Engine skill badge with proficiency rating
- Songwriting badges with per-criterion ratings
- Score, Status, Date

Storage is history-safe: every benchmark result is inserted as a new row with its `run_id` and `run_number`. The Results and Ranking pages aggregate the latest result per model/category/prompt, while the Comparisons page can inspect historical run-to-run changes.

### View Comparisons

The **Comparisons** page provides deeper visual analysis:

- **Best Model**, **Fastest Model (Elapsed)**, and **Best Coding Model** cards based on the currently filtered results. The Fastest Model card is determined by the lowest average `elapsed_seconds` of the run (i.e. the model that completed its benchmark in the shortest wall-clock time)
- **Badge Scores by Model** canvas chart using the same good/medium/bad/none colors as the Results badges
- **Blind Analysis vs. Self-Validation** canvas chart showing Run 1 score, Self-Validation score, and whether the final answer improved or got worse
- **Run History by Model and Category** line chart showing whether repeated runs improved or regressed
- **Truth-Audit Separate** chart that only includes `truth_audit` prompts and does not mix them into the other score charts
- **Run-to-Run Comparison** table showing better/worse deltas for the same model, category, and prompt

Hovering over rows in the Badge Scores and Self-Validation charts shows the full model name and score details.

---

## Benchmark System

### Multi-Pass Evaluation

**Run 1 (Blind):** Model receives the prompt without hints.

**Run 2 (Self-Validation):** Model reviews its own Run-1 answer with specific validation hints and improves it.

This approach, inspired by the SuperCalc security benchmark, measures:
- Baseline performance (Run 1)
- Self-reflection capability (Run 2)
- Consistency between runs

### Score Calculation

```
final_score = quality x 0.30
            + consistency x 0.20
            + performance x 0.20
            + format x 0.15
            + stability x 0.10
            + context x 0.05
```

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Quality** | 30% | Response quality (structure, completeness, relevance, technical accuracy) |
| **Consistency** | 20% | Similarity between Run 1 and Run 2 |
| **Performance** | 20% | Speed (Generation tok/s, Prompt tok/s, Latency) |
| **Format** | 15% | Format validation (JSON, code syntax, reasoning structure) |
| **Stability** | 10% | Variability across multiple runs |
| **Context** | 5% | Context size bonus |

### General Test Badges

General tests use compact icon badges in the Results and Ranking tables:

| Test | Badge Icon |
|------|------------|
| Coding Test | Code |
| Reasoning Test | Diagram |
| Long Context Test | Document |
| German Text Test | Translate |
| JSON Test | Braces |

Badge colors follow the same rating thresholds used by the other benchmark domains.

### Language Score Calculation

```
language_score = quality x 0.45
               + format x 0.25
               + syntax x 0.20
               + required_checks x 0.10
```

| Rating | Score | Badge Color |
|--------|-------|-------------|
| Good | >= 75 | Green |
| Medium | >= 45 | Orange |
| Weak | < 45 | Red |

### Engine Score Calculation

```
engine_score = quality x 0.45
             + format x 0.25
             + engine_syntax x 0.20
             + required_checks x 0.10
```

| Rating | Score | Badge Color |
|--------|-------|-------------|
| Good | >= 75 | Green |
| Medium | >= 45 | Orange |
| Weak | < 45 | Red |

### Songwriting Score Calculation

Songwriting tests are loaded from `sogmaker.md` and stored under the `songwriting_tests` category. Each result stores an overall songwriting score plus separate criterion scores:

```
songwriting_score = hook x 0.18
                  + rhyme x 0.12
                  + meter x 0.15
                  + emotion x 0.15
                  + structure x 0.15
                  + originality x 0.12
                  + suno_format x 0.08
                  + required_checks x 0.05
```

| Criterion | Badge | Description |
|-----------|-------|-------------|
| Hook | Music note | Catchiness, repetition, memorable short lines |
| Rhyme | Quote | End-rhyme and natural rhyme patterns |
| Meter | Soundwave | Short rhythmic lines and singability |
| Emotion | Heart | Clear emotional focus and lyrical feeling |
| Structure | Diagram | Section tags, verse/chorus/bridge flow, song progression |
| Originality | Stars | Fresh wording and low cliche usage |
| Suno Format | Music file | Section tags and Suno/AI-music-ready formatting |

| Rating | Score | Badge Color |
|--------|-------|-------------|
| Good | >= 75 | Green |
| Medium | >= 45 | Orange |
| Weak | < 45 | Red |

### Truth-Audit Benchmarks

Truth-Audit prompts are stored under the `truth_audit` category and are shown separately on the Comparisons page. They are intentionally excluded from the regular score comparison charts so factuality-oriented audits can be reviewed on their own.

Current Truth-Audit prompts:

| Prompt | Purpose |
|--------|---------|
| Truth-Audit - Claim Check | Labels claims as likely true, likely false, mixed/uncertain, or unverifiable |
| Truth-Audit - Contradiction Detection | Finds contradictions, unsupported claims, risky assumptions, and safer statements |
| Truth-Audit - Hallucination Resistance | Checks whether the model avoids inventing missing facts |

### Stability

| Condition | Score |
|-----------|-------|
| No errors | 100 |
| Minor errors (<=20%) | 75 |
| Moderate errors (<=40%) | 50 |
| Multiple errors (<=60%) | 25 |
| Completely failed (>60%) | 0 |

### Context Bonus

```
context_score = min(context_size / 1000, 100)
```

---

## Test Prompts

**Total: 141+ prompts across 5 categories**

### General Prompts (5)

| Prompt | Purpose | Key Checks |
|--------|---------|------------|
| Coding Test | Write Python function | def, return, try/except, docstring |
| Reasoning Test | Mathematical/logical task | Calculation, result, explanation |
| Long Context Test | Summarize long texts | >=3 risks, >=3 improvements, structure |
| German Text Test | Technical explanation in German | German words, >=3 reasons, clarity |
| JSON Test | Create valid JSON configuration | Valid JSON, all required keys |

### Truth-Audit Prompts (3)

| Prompt | Purpose | Key Checks |
|--------|---------|------------|
| Truth-Audit - Claim Check | Factual reliability audit | claim labels, uncertainty, external verification, no guessing |
| Truth-Audit - Contradiction Detection | Contradiction and assumption audit | contradictions, unsupported claims, safer statements, structured audit |
| Truth-Audit - Hallucination Resistance | Grounded answering under missing information | unknown handling, no hallucination, context grounding, direct answers |

### Multi-Language Coding Prompts (17 languages, 3 prompts each, 51 total)

| Language | Prompts |
|----------|---------|
| **Python** | Data Processing, Async API Client, CLI Tool |
| **JavaScript** | Array/Object Logic, Async Fetch Cache, DOM Component |
| **TypeScript** | Strong Typing, API Response Validation, State Manager |
| **Java** | Service Class, Multithreading, File Parser |
| **C#** | LINQ Data Processing, Async HTTP Client, Repository Pattern |
| **C++** | Modern C++ Data Processing, Memory Safety, Algorithm Task |
| **C** | String Parser, File Statistics, Simple Hash Table |
| **Go** | Concurrent Worker Pool, HTTP API Server, Log Parser |
| **Rust** | Ownership and Error Handling, CLI Parser, Struct and Traits |
| **PHP** | Form Validation, Simple Router, Database Layer |
| **Ruby** | Data Transformation, CLI Script, Class Design |
| **Kotlin** | Data Classes, Coroutines, Null Safety |
| **Swift** | Model and Filtering, Async/Await, Protocols |
| **Dart** | List Processing, Async Future Handling, Flutter Widget |
| **SQL** | Sales Query, Duplicate Detection, Monthly Report |
| **Bash** | Backup Script, Log Scanner, Process Monitor |
| **PowerShell** | System Report, File Cleanup, Service Checker |

### Game Engine & Graphics Programming Prompts (19 domains, 30+ prompts)

| Domain | Prompts |
|--------|---------|
| **Vulkan** | Triangle/Swapchain/Synchronization, Texture Upload/Layout Transitions, Descriptor Sets/Uniform Buffers, Synchronization Bug Fix |
| **GLSL** | PBR Fragment Shader, Tangent Space Normal Mapping, Shadow Mapping, Compute Shader Particles |
| **HLSL** | Blinn-Phong Lighting Shader |
| **DirectX 12** | Resource Barriers |
| **OpenGL** | Deferred Rendering, Instanced Rendering |
| **WebGPU** | Triangle with WGSL |
| **Render Pipeline** | Forward+ Renderer Design, Render Graph Architecture, HDR and Post-Processing |
| **Shader Debugging** | Black Screen Debugging, Wrong Lighting/Normals Debug |
| **GPU Performance** | Bottleneck Diagnosis, Draw Calls/Batching/Instancing, VRAM and Texture Optimization |
| **Unity** | URP Custom Render Feature, Job System and Burst, Addressables and Scene Streaming |
| **Unreal** | C++ Actor Replication, Gameplay Ability System, Render Dependency Graph |
| **Godot** | Nodes/Scenes/Signals, Water Shader, RenderingDevice Compute |
| **Physics** | AABB Collision System, Broadphase Spatial Partitioning |
| **Multiplayer** | Client Prediction/Server Reconciliation, Snapshot Interpolation |
| **Asset Pipeline** | glTF Import, Texture Compression |
| **Editor Tools** | Level Validation, Runtime Debug Overlay |
| **Gameplay Systems** | Inventory System, Save/Load System |
| **2D Engine** | Tilemap Renderer, Pixel-Perfect Camera |
| **3D Engine** | Skeletal Animation System, LOD/Occlusion/Scene Streaming |

### Songwriting Prompts (52 prompts)

Songwriting prompts are loaded from `sogmaker.md` and grouped in the UI as **Songwriting Tests**.

| Domain | Examples |
|--------|----------|
| **Hook** | English pop chorus, Greek pop chorus, German pop chorus |
| **Chorus** | Emotional release, multiple chorus variants with strong final lines |
| **Verse / Pre-Chorus / Bridge** | Story setup, tension build, emotional turn |
| **Full Song Structure** | Radio-ready pop, Greek Suno-ready pop/laiko, German pop-rap |
| **Rhyme** | Clean end rhymes, Greek natural rhymes, rhyme repair |
| **Meter and Singability** | 128 BPM dance-pop, Greek singable verse and chorus |
| **Storytelling and Emotion** | Story progression, regret-only section, euphoric EDM chorus/drop |
| **Genre Control** | Greek laiko, German rap, Frenchcore, K-pop, Reggaeton |
| **Suno / AI-Music Format** | Suno-ready Greek pop, EDM drop format, short Suno style prompts |
| **Rewrite and Originality** | Improve weak choruses, naturalize Greek, avoid cliches |
| **Multilingual Lyrics** | German, English, Greek, Spanish, French, Polish, Turkish, Albanian, Dutch, Korean/K-pop |

See `prompts.md` for detailed evaluation criteria and examples.
See `engine.md` for game engine benchmark specifications.
See `sogmaker.md` for songwriting benchmark prompts and criteria.

---

## Project Structure

```
LLM-Benchmark/
├── app.py                 # FastAPI main application
├── database.py            # SQLite database operations
├── benchmark.py           # Benchmark logic and prompts
├── scoring.py             # Traceable multi-dimensional scoring
├── llama_client.py        # llama-server client
├── requirements.txt       # Python dependencies
├── start.bat              # Windows start script
├── start.sh               # Linux/macOS start script
├── README.md              # This file
├── changes.md             # Feature changelog
├── prompts.md             # Prompt descriptions and evaluation criteria
├── engine.md              # Game engine benchmark specifications
├── sogmaker.md            # Songwriting benchmark prompts and criteria
│
├── logs/                  # Log files
│   └── benchmark.log
│
├── templates/             # HTML templates
│   ├── base.html          # Base layout
│   ├── dashboard.html     # Dashboard page
│   ├── benchmark.html     # Benchmark start page
│   ├── results.html       # Results table
│   ├── ranking.html       # Ranking table
│   └── comparisons.html   # Detailed comparison charts
│
├── static/                # Static files
│   ├── css/dark.css       # Dark theme styling
│   ├── js/app.js          # Frontend logic
│   └── sounds/done.mp3    # Completion sound (optional)
│
└── data/                  # SQLite database
    └── benchmarks.db
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard |
| GET | `/benchmark` | Benchmark page |
| GET | `/results` | Results page |
| GET | `/ranking` | Ranking page |
| GET | `/comparisons` | Detailed comparison page |
| GET | `/api/health` | Check server connection |
| GET | `/api/prompts` | Available prompts (with category, language, engine_skill, songwriting_skill, difficulty) |
| GET | `/api/prompts/engine-quick-test` | Engine quick test set (10 prompts) |
| GET | `/api/language-badges` | Language badges grouped by model |
| GET | `/api/engine-badges` | Engine skill badges grouped by model |
| POST | `/api/benchmark/start` | Start benchmark |
| GET | `/api/benchmark/status/{id}` | Live status |
| POST | `/api/benchmark/abort/{id}` | Abort benchmark |
| GET | `/api/results` | All results (JSON) |
| GET | `/api/results/{id}` | Single result |
| DELETE | `/api/results/{id}` | Delete result |
| POST | `/api/results/{id}/quality-score` | Update quality score |
| GET | `/api/ranking` | Ranking (JSON) |
| GET | `/api/models` | All models |
| GET | `/api/stats` | Dashboard statistics |

---

## Error Handling

The app never crashes. The following errors are caught:

- llama-server not reachable
- Timeout on requests
- Invalid server URL
- Empty response from server
- JSON parsing errors
- Missing token information
- Missing `nvidia-smi`
- Database errors

Every error is saved to the database and log file.

---

## Configuration

The server URL can be set via the `LLAMA_SERVER_URL` environment variable:

```bash
# Windows
set LLAMA_SERVER_URL=http://192.168.1.100:8080

# Linux/macOS
export LLAMA_SERVER_URL=http://192.168.1.100:8080
```

Benchmark parameter input supports localized decimal notation:

| Field | Range | Accepted Examples |
|-------|-------|-------------------|
| Temperature | `0` to `2` | `0.7`, `0,7`, `0.95`, `0,95` |
| Top-P | `0` to `1` | `0.9`, `0,9`, `0.900`, `0,900` |

---

## Documentation

| File | Content |
|------|---------|
| `prompts.md` | All test prompts with evaluation criteria, examples, and extension guide |
| `engine.md` | Game engine and graphics programming benchmark specifications with 30+ prompts |
| `sogmaker.md` | Songwriting benchmark prompts, checks, metadata, and badge criteria |
