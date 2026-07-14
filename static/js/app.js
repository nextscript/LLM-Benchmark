/**
 * LLM Benchmark - Frontend JavaScript
 */

// ── Language Icon & Rating Mappings ──

const languageIconMap = {
    python: 'devicon-python-plain',
    javascript: 'devicon-javascript-plain',
    typescript: 'devicon-typescript-plain',
    java: 'devicon-java-plain',
    csharp: 'devicon-csharp-plain',
    cpp: 'devicon-cplusplus-plain',
    c: 'devicon-c-plain',
    go: 'devicon-go-plain',
    rust: 'devicon-rust-plain',
    php: 'devicon-php-plain',
    ruby: 'devicon-ruby-plain',
    kotlin: 'devicon-kotlin-plain',
    swift: 'devicon-swift-plain',
    dart: 'devicon-dart-plain',
    sql: 'devicon-sqldeveloper-plain',
    bash: 'devicon-bash-plain',
    powershell: 'devicon-powershell-plain',
};

const ratingLabelMap = {
    good: 'Can do well',
    medium: 'Can do medium',
    bad: 'Can do poorly',
};

const generalTestBadgeMap = {
    coding: { label: 'Coding Test', short: 'Code', icon: 'bi bi-code-slash' },
    reasoning: { label: 'Reasoning Test', short: 'Logic', icon: 'bi bi-diagram-2' },
    long_context: { label: 'Long Context Test', short: 'Ctx', icon: 'bi bi-file-earmark-text' },
    german_text: { label: 'German Text Test', short: 'DE', icon: 'bi bi-translate' },
    json_test: { label: 'JSON Test', short: 'JSON', icon: 'bi bi-braces' },
};

const engineSkillLabelMap = {
    vulkan: 'Vulkan',
    glsl: 'GLSL',
    hlsl: 'HLSL',
    opengl: 'OpenGL',
    directx12: 'DirectX 12',
    webgpu: 'WebGPU',
    unity: 'Unity',
    unreal: 'Unreal',
    godot: 'Godot',
    render_pipeline: 'Rendering',
    shader_debugging: 'Shader',
    gpu_performance: 'Optimization',
    physics: 'Physics',
    multiplayer: 'Multiplayer',
    asset_pipeline: 'Asset Pipeline',
    editor_tools: 'Editor Tools',
    gameplay_systems: 'Gameplay',
    '2d': '2D Engine',
    '3d': '3D Engine',
};

const engineIconMap = {
    vulkan: 'bi bi-triangle',
    glsl: 'bi bi-braces',
    hlsl: 'bi bi-code-square',
    opengl: 'bi bi-circle-square',
    directx12: 'bi bi-windows',
    webgpu: 'bi bi-gpu-card',
    unity: 'devicon-unity-plain',
    unreal: 'devicon-unrealengine-original',
    godot: 'devicon-godot-plain',
    render_pipeline: 'bi bi-diagram-3',
    shader_debugging: 'bi bi-bug',
    gpu_performance: 'bi bi-speedometer2',
    physics: 'bi bi-bezier2',
    multiplayer: 'bi bi-people',
    asset_pipeline: 'bi bi-box-seam',
    editor_tools: 'bi bi-tools',
    gameplay_systems: 'bi bi-controller',
    '2d': 'bi bi-square',
    '3d': 'bi bi-box',
};

const songwritingCriterionMap = {
    hook: { label: 'Hook', field: 'songwriting_hook_score', icon: 'bi bi-music-note-beamed' },
    rhyme: { label: 'Rhyme', field: 'songwriting_rhyme_score', icon: 'bi bi-quote' },
    meter: { label: 'Meter', field: 'songwriting_meter_score', icon: 'bi bi-soundwave' },
    emotion: { label: 'Emotion', field: 'songwriting_emotion_score', icon: 'bi bi-heart' },
    structure: { label: 'Structure', field: 'songwriting_structure_score', icon: 'bi bi-diagram-3' },
    originality: { label: 'Originality', field: 'songwriting_originality_score', icon: 'bi bi-stars' },
};

const songwritingPromptBadgeMap = {
    songwriting_language_english_indie_pop: { label: 'English - Indie Pop', short: 'EN', match: ['english', 'indie pop', 'indie_pop'] },
    songwriting_language_spanish_reggaeton: { label: 'Spanish - Reggaeton Pop', short: 'ES', match: ['spanish', 'reggaeton'] },
    songwriting_language_french_chanson_pop: { label: 'French - Chanson Pop', short: 'FR', match: ['french', 'chanson'] },
    songwriting_language_italian_italo_disco: { label: 'Italian - Italo Disco', short: 'IT', match: ['italian', 'italo disco', 'italo_disco'] },
    songwriting_language_dutch_nederpop: { label: 'Dutch - Nederpop', short: 'NL', match: ['dutch', 'nederpop'] },
    songwriting_language_polish_synth_pop: { label: 'Polish - Synth Pop', short: 'PL', match: ['polish', 'synth pop', 'synth_pop'] },
    songwriting_language_turkish_arabesque_pop: { label: 'Turkish - Arabesque Pop', short: 'TR', match: ['turkish', 'arabesque'] },
    songwriting_language_greek_laiko_pop: { label: 'Greek - Laiko Pop', short: 'EL', match: ['greek', 'laiko'] },
    songwriting_language_korean_kpop: { label: 'K-Pop - Korean/English', short: 'KP', match: ['korean', 'k-pop', 'kpop'] },
};

const songwritingRatingLabelMap = {
    good: 'Strong',
    medium: 'Moderate',
    bad: 'Weak',
    none: 'Not tested',
};

// ── Language Badge ──

function languageBadge(r) {
    if (!r.programming_language) {
        return '<span class="text-muted">-</span>';
    }
    const lang = String(r.programming_language).toLowerCase();
    const label = esc(r.programming_language_label || lang);
    const rating = r.language_rating || 'bad';
    const score = Number(r.language_score || 0).toFixed(0);
    const iconClass = languageIconMap[lang];
    const icon = iconClass
        ? `<i class="${iconClass} lang-badge-icon"></i>`
        : `<span class="lang-badge-fallback">${label.charAt(0).toUpperCase()}</span>`;

    return `
        <span class="lang-badge lang-badge-${rating}" title="${label}: ${score}/100">
            ${icon}
        </span>
    `;
}

// ── Language Badges (multiple per model) ──

function languageBadges(list) {
    if (!Array.isArray(list) || list.length === 0) {
        return '<span class="text-muted">-</span>';
    }
    return `<div class="lang-badge-wrap">${list.map(function(b) {
        const iconClass = languageIconMap[b.language];
        const icon = iconClass
            ? `<i class="${iconClass} lang-badge-icon"></i>`
            : `<span class="lang-badge-fallback">${(b.language_label || b.language).charAt(0).toUpperCase()}</span>`;
        return `<span class="lang-badge lang-badge-${b.rating || 'bad'}" title="${b.language_label || b.language}: ${b.score || 0}/100">
            ${icon}
        </span>`;
    }).join('')}</div>`;
}

// ── Engine Badge (single result) ──

function engineBadge(r) {
    if (!r.engine_skill) {
        return '<span class="text-muted">-</span>';
    }
    const skill = String(r.engine_skill).toLowerCase();
    const label = esc(r.engine_skill_label || engineSkillLabelMap[skill] || skill);
    const rating = r.engine_rating || 'bad';
    const ratingText = r.engine_rating_label || ratingLabelMap[rating] || 'Can do poorly';
    const score = Number(r.engine_score || 0).toFixed(0);

    return `
        <span class="engine-badge engine-badge-${rating}" title="${label}: ${ratingText} (${score}/100)">
            <span class="engine-badge-icon"><i class="bi bi-gpu-card"></i></span>
            <span class="engine-badge-name">${label}</span>
            <span class="engine-badge-rating">${ratingText}</span>
        </span>
    `;
}

// ── Engine Badges (multiple per model) ──

function engineBadges(list) {
    if (!Array.isArray(list) || list.length === 0) {
        return '<span class="text-muted">-</span>';
    }
    return `<div class="engine-badge-wrap">${list.map(function(b) {
        const label = b.engine_skill_label || engineSkillLabelMap[b.engine_skill] || b.engine_skill;
        const iconClass = engineIconMap[b.engine_skill] || 'bi bi-gpu-card';
        return `<span class="engine-badge engine-badge-${b.rating || 'bad'}" title="${label}: ${b.rating_label || ratingLabelMap[b.rating] || 'Can do poorly'} (${b.score || 0}/100)">
            <i class="${iconClass} engine-badge-icon"></i>
        </span>`;
    }).join('')}</div>`;
}

// ── Check server health ──

async function checkServerHealth() {
    const spinner = document.getElementById('healthSpinner');
    const text = document.getElementById('healthText');
    const serverUrl = document.getElementById('server_url')?.value || 'http://127.0.0.1:8080';
    
    if (!spinner) return;
    
    spinner.classList.add('spinner-border', 'spinner-border-sm');
    text.textContent = 'Checking connection...';
    
    try {
        const resp = await fetch(`/api/health?server_url=${encodeURIComponent(serverUrl)}`);
        const data = await resp.json();
        
        if (data.reachable) {
            spinner.className = 'text-success me-2';
            spinner.classList.remove('spinner-border', 'spinner-border-sm');
            spinner.innerHTML = '<i class="bi bi-check-circle-fill"></i>';
            text.textContent = `Server reachable: ${data.server_url}`;
            text.className = 'text-success';
        } else {
            spinner.className = 'text-danger me-2';
            spinner.classList.remove('spinner-border', 'spinner-border-sm');
            spinner.innerHTML = '<i class="bi bi-x-circle-fill"></i>';
            text.textContent = `Server not reachable: ${data.server_url}`;
            text.className = 'text-danger';
        }
    } catch (err) {
        spinner.className = 'text-danger me-2';
        spinner.classList.remove('spinner-border', 'spinner-border-sm');
        spinner.innerHTML = '<i class="bi bi-x-circle-fill"></i>';
        text.textContent = 'Connection failed.';
        text.className = 'text-danger';
    }
}

async function loadLlamaConfig(showErrors = true) {
    const serverUrlInput = document.getElementById('server_url');
    const status = document.getElementById('llamaConfigStatus');
    const loadBtn = document.getElementById('loadLlamaConfigBtn');
    if (!serverUrlInput) return;

    const serverUrl = serverUrlInput.value || 'http://127.0.0.1:8080';
    if (status) {
        status.textContent = 'Loading values from llama-server...';
        status.className = 'form-text text-muted';
    }
    if (loadBtn) {
        loadBtn.disabled = true;
    }

    try {
        const resp = await fetch(`/api/llama-config?server_url=${encodeURIComponent(serverUrl)}`);
        const data = await resp.json();
        if (!resp.ok || !data.ok) {
            if (showErrors && status) {
                status.textContent = 'No configuration values found on llama-server.';
                status.className = 'form-text text-warning';
            } else if (status) {
                status.textContent = 'Load values from llama-server.';
                status.className = 'form-text';
            }
            return;
        }

        applyLlamaConfig(data);
        if (status) {
            status.textContent = '';
            status.className = 'form-text';
        }
    } catch (err) {
        if (showErrors && status) {
            status.textContent = 'Could not load values from llama-server.';
            status.className = 'form-text text-danger';
        }
        console.error('llama config load failed:', err);
    } finally {
        if (loadBtn) {
            loadBtn.disabled = false;
        }
    }
}

function applyLlamaConfig(data) {
    setInputValue('model_name', data.model_name);
    setInputValue('context_size', data.context_size);
    setInputValue('max_tokens', data.max_tokens);
    setInputValue('temperature', data.temperature);
    setInputValue('top_p', data.top_p);
}

function setInputValue(id, value) {
    if (value === undefined || value === null || value === '') return;
    const input = document.getElementById(id);
    if (input) {
        input.value = value;
    }
}

// ── Load dashboard statistics ──

async function loadDashboardStats() {
    try {
        const resp = await fetch('/api/stats');
        const stats = await resp.json();
        
        const el = (id) => document.getElementById(id);
        
        el('totalModels').textContent = stats.total_models || 0;
        
        if (stats.best_model) {
            const avgScore = stats.best_model.avg_final_score ? stats.best_model.avg_final_score.toFixed(2) : '-';
            const testCount = stats.best_model.test_count || 0;
            el('bestModel').innerHTML = `
                <div>${esc(stats.best_model.model_name)}</div>
                <small class="text-muted">${avgScore} avg score (${testCount} tests)</small>
            `;
        } else {
            el('bestModel').textContent = '-';
        }

        if (stats.fastest_elapsed_model) {
            const avgElapsed = stats.fastest_elapsed_model.avg_elapsed != null ? formatElapsed(stats.fastest_elapsed_model.avg_elapsed) : '-';
            const minElapsed = stats.fastest_elapsed_model.min_elapsed != null ? formatElapsed(stats.fastest_elapsed_model.min_elapsed) : '-';
            const testCount = stats.fastest_elapsed_model.test_count || 0;
            el('fastestModel').innerHTML = `
                <div>${esc(stats.fastest_elapsed_model.model_name)}</div>
                <small class="text-muted">avg ${avgElapsed} (${testCount} tests, best ${minElapsed})</small>
            `;
        } else {
            el('fastestModel').textContent = '-';
        }

        if (stats.best_coding_model) {
            const badgeInfo = stats.best_coding_model;
            const totalBadges = Object.keys(languageIconMap).length +
                               Object.keys(generalTestBadgeMap).length +
                               Object.keys(engineSkillLabelMap).length;
            el('codingModel').innerHTML = `
                <div>${esc(badgeInfo.model_name)}</div>
                <small class="text-muted">${badgeInfo.total_good_badges}/${totalBadges} good badges total</small>
            `;
        } else {
            el('codingModel').textContent = '-';
        }
        
        // Last benchmark
        const lastEl = el('lastBenchmark');
        if (stats.last_benchmark) {
            lastEl.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>Model:</span> <strong>${esc(stats.last_benchmark.model_name)}</strong>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Score:</span> <strong>${esc(stats.last_benchmark.final_score)}</strong>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Gen tok/s:</span> <strong>${esc(stats.last_benchmark.generation_tokens_per_second)}</strong>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Date:</span> <small class="text-muted">${formatDate(stats.last_benchmark.created_at)}</small>
                </div>
            `;
        } else {
            lastEl.innerHTML = '<p class="text-muted">No benchmarks yet.</p>';
        }
        
        // Last error
        const errEl = el('lastError');
        if (stats.last_error) {
            errEl.innerHTML = `
                <div class="text-danger">
                    <i class="bi bi-exclamation-circle"></i> ${esc(stats.last_error.error_message || 'Unknown error')}
                </div>
                <small class="text-muted">${formatDate(stats.last_error.created_at)}</small>
            `;
        } else {
            errEl.innerHTML = '<p class="text-muted">No errors known.</p>';
        }
    } catch (err) {
        console.error('Error loading statistics:', err);
    }
}

// ── Dynamic prompt loading ──

let allPrompts = [];

async function loadPrompts() {
    try {
        const resp = await fetch('/api/prompts');
        allPrompts = await resp.json();
        buildPromptSelect('all');
    } catch (err) {
        console.error('Error loading prompts:', err);
    }
}

function buildPromptSelect(category) {
    const select = document.getElementById('prompt_keys');
    if (!select) return;
    
    let filtered = allPrompts;
    if (category !== 'all') {
        filtered = allPrompts.filter(p => p.category === category);
    }
    
    const groups = {};
    filtered.forEach(p => {
        let group;
        if (p.category === 'coding_language') {
            group = p.language_label || p.language || 'Other';
        } else if (p.category === 'game_engine') {
            group = p.engine_skill_label || engineSkillLabelMap[p.engine_skill] || 'Engine';
        } else if (p.category === 'songwriting_tests') {
            group = p.sub_category || p.songwriting_skill_label || 'Songwriting';
        } else if (p.category === 'truth_audit') {
            group = 'Truth-Audit';
        } else {
            group = p.category || 'General';
        }
        if (!groups[group]) groups[group] = [];
        groups[group].push(p);
    });

    if (category === 'songwriting_tests') {
        const languagePrompts = filtered.filter(p => songwritingPromptBadgeMap[p.key]);
        if (groups.Language) {
            groups.Language = groups.Language.map(p => {
                const badge = songwritingPromptBadgeMap[p.key];
                if (!badge) return p;
                return {
                    ...p,
                    name: `Language: ${badge.short} - ${p.genre || p.name}`,
                };
            });
        }
        Object.keys(groups).forEach(group => {
            if (group === 'Language') return;
            const existingKeys = new Set(groups[group].map(p => p.key));
            languagePrompts.forEach(p => {
                if (!existingKeys.has(p.key)) {
                    const badge = songwritingPromptBadgeMap[p.key];
                    groups[group].push({
                        ...p,
                        name: `${group}: ${badge.short} - ${p.genre || p.name}`,
                    });
                }
            });
        });
    }
    
    let html = '';
    for (const [group, prompts] of Object.entries(groups)) {
        if (prompts.length === 1) {
            const p = prompts[0];
            const selected = p.defaultSelected ? ' selected' : '';
            html += `<option value="${p.key}"${selected}>${p.name}</option>`;
        } else {
            html += `<optgroup label="${group}">`;
            prompts.forEach(p => {
                const selected = p.defaultSelected ? ' selected' : '';
                html += `<option value="${p.key}"${selected}>${p.name}</option>`;
            });
            html += '</optgroup>';
        }
    }
    
    select.innerHTML = html;
}

document.getElementById('prompt_category')?.addEventListener('change', function() {
    buildPromptSelect(this.value);
});

// ── Benchmark form ──

let benchmarkPollInterval = null;
let benchmarkStartTime = null;
const BENCHMARK_RUN_STORAGE_KEY = 'llmBenchmarkCurrentRunId';
const BENCHMARK_STATUS_POLL_MS = 1000;

function initBenchmarkForm() {
    const form = document.getElementById('benchmarkForm');
    const startBtn = document.getElementById('startBtn');
    const abortBtn = document.getElementById('abortBtn');
    const loadConfigBtn = document.getElementById('loadLlamaConfigBtn');
    const serverUrlInput = document.getElementById('server_url');
    
    if (!form) return;

    if (loadConfigBtn) {
        loadConfigBtn.addEventListener('click', function() {
            checkServerHealth();
            loadLlamaConfig(true);
        });
    }

    if (serverUrlInput) {
        serverUrlInput.addEventListener('change', function() {
            checkServerHealth();
        });
    }

    loadLlamaConfig(false);
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        const promptSelect = document.getElementById('prompt_keys');
        const selectedPrompts = Array.from(promptSelect.selectedOptions).map(o => o.value);
        formData.set('prompt_keys', selectedPrompts.join(','));
        
        const selfValCheckbox = document.getElementById('enable_self_validation');
        formData.set('enable_self_validation', selfValCheckbox && selfValCheckbox.checked ? 'true' : 'false');
        
        startBtn.disabled = true;
        startBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Starting...';
        abortBtn.style.display = 'inline-block';
        
        // Show status card
        const statusCard = document.getElementById('statusCard');
        statusCard.style.display = 'block';
        statusCard.classList.add('benchmark-running');
        
        benchmarkStartTime = Date.now();
        startElapsedTimer();
        
        try {
            const resp = await fetch('/api/benchmark/start', {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();
            
            if (data.status === 'failed') {
                document.getElementById('statusTitle').textContent = 'Error';
                document.getElementById('statusStep').textContent = data.message || 'Benchmark failed.';
                document.getElementById('progressBar').style.width = '0%';
                document.getElementById('progressBar').classList.remove('progress-bar-animated');
                document.getElementById('progressBar').classList.add('bg-danger');
                return;
            }
            
            // Start polling
            window._currentRunId = data.run_id;
            rememberBenchmarkRun(data.run_id);
            benchmarkPollInterval = setInterval(() => pollBenchmarkStatus(data.run_id), BENCHMARK_STATUS_POLL_MS);
            pollBenchmarkStatus(data.run_id);
            
        } catch (err) {
            document.getElementById('statusTitle').textContent = 'Error';
            document.getElementById('statusStep').textContent = err.message;
            document.getElementById('progressBar').classList.add('bg-danger');
        }
    });
    
    if (abortBtn) {
        abortBtn.addEventListener('click', async function() {
            if (benchmarkPollInterval) {
                clearInterval(benchmarkPollInterval);
            }
            
            const currentRunId = window._currentRunId;
            if (currentRunId) {
                try {
                    const resp = await fetch(`/api/benchmark/abort/${currentRunId}`, { method: 'POST' });
                    const data = await resp.json();
                    console.log('Abort response:', data);
                } catch (err) {
                    console.error('Abort failed:', err);
                }
            }
            
            // Reset UI immediately
            document.getElementById('statusTitle').textContent = 'Aborted';
            document.getElementById('statusStep').textContent = 'Benchmark was aborted.';
            document.getElementById('statusSpinner').classList.remove('spinner-border', 'text-info');
            document.getElementById('statusSpinner').classList.add('text-danger');
            document.getElementById('statusSpinner').innerHTML = '<i class="bi bi-x-circle-fill"></i>';
            document.getElementById('progressBar').classList.remove('progress-bar-animated', 'bg-info');
            document.getElementById('progressBar').classList.add('bg-danger');
            document.getElementById('progressPercent').textContent = '0%';
            document.getElementById('tokensPerSec').textContent = '-';
            document.getElementById('decodedTokens').textContent = '-';
            document.getElementById('metricSource').textContent = '-';
            
            // Stop timer
            if (window._elapsedInterval) {
                clearInterval(window._elapsedInterval);
            }
            
            // Reset buttons
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Start Benchmark';
            abortBtn.style.display = 'none';
            forgetBenchmarkRun();
        });
    }

    resumeActiveBenchmark();
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            resumeActiveBenchmark();
        }
    });
}

function rememberBenchmarkRun(runId) {
    if (!runId) return;
    window._currentRunId = runId;
    localStorage.setItem(BENCHMARK_RUN_STORAGE_KEY, String(runId));
}

function forgetBenchmarkRun() {
    window._currentRunId = null;
    localStorage.removeItem(BENCHMARK_RUN_STORAGE_KEY);
}

async function resumeActiveBenchmark() {
    const storedRunId = localStorage.getItem(BENCHMARK_RUN_STORAGE_KEY);
    let activeRun = null;

    if (storedRunId) {
        activeRun = await fetchBenchmarkRun(storedRunId);
    }

    if (!activeRun || !isActiveBenchmarkStatus(activeRun.status)) {
        activeRun = await fetchActiveBenchmark();
    }

    if (!activeRun || !isActiveBenchmarkStatus(activeRun.status)) {
        forgetBenchmarkRun();
        return;
    }

    prepareRunningBenchmarkUi(activeRun);
    rememberBenchmarkRun(activeRun.id);
    pollBenchmarkStatus(activeRun.id);
    if (benchmarkPollInterval) {
        clearInterval(benchmarkPollInterval);
    }
    benchmarkPollInterval = setInterval(() => pollBenchmarkStatus(activeRun.id), BENCHMARK_STATUS_POLL_MS);
}

async function fetchBenchmarkRun(runId) {
    try {
        const resp = await fetch(`/api/benchmark/status/${runId}`);
        if (!resp.ok) return null;
        return await resp.json();
    } catch (err) {
        console.error('Could not load stored benchmark:', err);
        return null;
    }
}

async function fetchActiveBenchmark() {
    try {
        const resp = await fetch('/api/benchmark/active');
        if (!resp.ok) return null;
        const data = await resp.json();
        return data.run || null;
    } catch (err) {
        console.error('Could not load active benchmark:', err);
        return null;
    }
}

function isActiveBenchmarkStatus(status) {
    return status === 'waiting' || status === 'running';
}

function prepareRunningBenchmarkUi(run) {
    const statusCard = document.getElementById('statusCard');
    const startBtn = document.getElementById('startBtn');
    const abortBtn = document.getElementById('abortBtn');
    const statusSpinner = document.getElementById('statusSpinner');
    const progressBar = document.getElementById('progressBar');

    if (statusCard) {
        statusCard.style.display = 'block';
        statusCard.classList.add('benchmark-running');
    }
    if (startBtn) {
        startBtn.disabled = true;
        startBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Running...';
    }
    if (abortBtn) {
        abortBtn.style.display = 'inline-block';
    }
    if (statusSpinner) {
        statusSpinner.className = 'spinner-border text-info me-3';
        statusSpinner.innerHTML = '<span class="visually-hidden">Running...</span>';
    }
    if (progressBar) {
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-info';
    }

    benchmarkStartTime = parseUtcDate(run.started_at)?.getTime() || Date.now();
    startElapsedTimer();
}

async function pollBenchmarkStatus(runId) {
    try {
        const resp = await fetch(`/api/benchmark/status/${runId}`);
        if (!resp.ok) {
            forgetBenchmarkRun();
            return;
        }
        const data = await resp.json();
        
        document.getElementById('statusTitle').textContent = formatStatus(data.status);
        document.getElementById('statusStep').textContent = data.current_step || '-';
        document.getElementById('progressBar').style.width = `${data.progress || 0}%`;
        document.getElementById('progressPercent').textContent = `${data.progress || 0}%`;
        
        const tokensEl = document.getElementById('tokensPerSec');
        const decodedEl = document.getElementById('decodedTokens');
        const sourceEl = document.getElementById('metricSource');
        
        if (data.status === 'running') {
            const tokensPerSecond = Number(data.tokens_per_second ?? 0);
            tokensEl.textContent = `${tokensPerSecond.toFixed(2)} tok/s`;
            tokensEl.className = tokensPerSecond > 0 ? 'text-info' : 'text-muted';
            if (data.decoded_tokens !== undefined && data.decoded_tokens !== null && Number(data.decoded_tokens) >= 0) {
                decodedEl.textContent = Number(data.decoded_tokens).toLocaleString('en-US');
                decodedEl.className = Number(data.decoded_tokens) > 0 ? 'text-info' : 'text-muted';
            } else {
                decodedEl.textContent = '-';
                decodedEl.className = 'text-muted';
            }
            sourceEl.textContent = data.metric_source || '-';
            sourceEl.className = data.metric_source === 'unavailable' ? 'text-muted' : 'text-info';
        } else if (data.status === 'finished') {
            tokensEl.textContent = '-';
            tokensEl.className = '';
            decodedEl.textContent = '-';
            decodedEl.className = '';
            sourceEl.textContent = '-';
            sourceEl.className = '';
        }
        
        if (data.status === 'finished') {
            clearInterval(benchmarkPollInterval);
            clearInterval(window._elapsedInterval);
            forgetBenchmarkRun();
            document.getElementById('statusSpinner').classList.remove('spinner-border');
            document.getElementById('statusSpinner').classList.add('text-success');
            document.getElementById('statusSpinner').innerHTML = '<i class="bi bi-check-circle-fill display-6"></i>';
            document.getElementById('progressBar').classList.remove('progress-bar-animated');
            document.getElementById('progressBar').classList.remove('bg-info');
            document.getElementById('progressBar').classList.add('bg-success');
            
            playDoneSound();
            
            setTimeout(() => {
                window.location.href = '/results';
            }, 1500);
        } else if (data.status === 'failed') {
            clearInterval(benchmarkPollInterval);
            clearInterval(window._elapsedInterval);
            forgetBenchmarkRun();
            document.getElementById('statusSpinner').classList.remove('spinner-border');
            document.getElementById('statusSpinner').classList.add('text-danger');
            document.getElementById('statusSpinner').innerHTML = '<i class="bi bi-x-circle-fill display-6"></i>';
            document.getElementById('progressBar').classList.remove('progress-bar-animated');
            document.getElementById('progressBar').classList.add('bg-danger');
            document.getElementById('statusStep').textContent = data.error_message || 'Error';
        }
    } catch (err) {
        console.error('Polling error:', err);
    }
}

// ── Helper: Group results by run_id ──

function groupByModelName(results) {
    const groups = {};
    results.forEach(r => {
        const modelName = r.model_name || `single_${r.id}`;
        if (!groups[modelName]) groups[modelName] = [];
        groups[modelName].push(r);
    });
    
    return Object.entries(groups).map(([modelName, runResults]) => {
        const latestByPrompt = new Map();
        runResults.forEach(r => {
            const key = `${r.prompt_category || 'general'}::${r.prompt_key || r.prompt_name || r.id}`;
            const existing = latestByPrompt.get(key);
            const currentTime = parseUtcDate(r.created_at)?.getTime() || 0;
            const existingTime = existing ? (parseUtcDate(existing.created_at)?.getTime() || 0) : -1;
            if (!existing || currentTime >= existingTime) {
                latestByPrompt.set(key, r);
            }
        });

        const currentResults = Array.from(latestByPrompt.values());
        const n = currentResults.length;
        const first = [...currentResults].sort((a, b) => {
            const aDate = parseUtcDate(a.created_at)?.getTime() || 0;
            const bDate = parseUtcDate(b.created_at)?.getTime() || 0;
            return bDate - aDate;
        })[0];
        
        if (n === 1) return first;
        
        const avg = (arr, key) => arr.reduce((sum, r) => sum + (r[key] || 0), 0) / arr.length;
        
        return {
            ...first,
            model_name: modelName,
            prompt_name: `Average (${n} prompts)`,
            generation_tokens_per_second: avg(currentResults, 'generation_tokens_per_second'),
            prompt_tokens_per_second: avg(currentResults, 'prompt_tokens_per_second'),
            quality_score: avg(currentResults, 'quality_score'),
            format_score: avg(currentResults, 'format_score'),
            consistency_score: avg(currentResults, 'consistency_score'),
            stability_score: avg(currentResults, 'stability_score'),
            final_score: avg(currentResults, 'final_score'),
            context_score: avg(currentResults, 'context_score'),
            first_token_latency: avg(currentResults, 'first_token_latency'),
            songwriting_score: avg(currentResults, 'songwriting_score'),
            songwriting_hook_score: avg(currentResults, 'songwriting_hook_score'),
            songwriting_rhyme_score: avg(currentResults, 'songwriting_rhyme_score'),
            songwriting_meter_score: avg(currentResults, 'songwriting_meter_score'),
            songwriting_emotion_score: avg(currentResults, 'songwriting_emotion_score'),
            songwriting_structure_score: avg(currentResults, 'songwriting_structure_score'),
            songwriting_originality_score: avg(currentResults, 'songwriting_originality_score'),
            _allResults: currentResults,
            _historyResults: runResults,
        };
    });
}

function getAllLanguageBadges(results) {
    const languageMap = new Map();

    Object.keys(languageIconMap).forEach(lang => {
        languageMap.set(lang, {
            language: lang,
            language_label: lang.charAt(0).toUpperCase() + lang.slice(1),
            scores: [],
            rating: 'none'
        });
    });
    
    results.forEach(r => {
        if (r.programming_language) {
            const lang = String(r.programming_language).toLowerCase();
            const score = Number(r.language_score || 0);
            
            if (languageMap.has(lang)) {
                languageMap.get(lang).scores.push(score);
            }
        }
    });
    
    const badges = Array.from(languageMap.values()).map(b => {
        let avgScore = 0;
        let rating = 'none';
        
        if (b.scores.length > 0) {
            avgScore = b.scores.reduce((sum, s) => sum + s, 0) / b.scores.length;
            if (avgScore >= 75) rating = 'good';
            else if (avgScore >= 45) rating = 'medium';
            else rating = 'bad';
        }
        
        return {
            ...b,
            score: avgScore,
            rating: rating
        };
    });

    return `<div class="lang-badge-wrap">${badges.map(b => {
        const iconClass = languageIconMap[b.language];
        const icon = iconClass
            ? `<i class="${iconClass} lang-badge-icon"></i>`
            : `<span class="lang-badge-fallback">${b.language_label.charAt(0).toUpperCase()}</span>`;
        return `<span class="lang-badge lang-badge-${b.rating}" title="${b.language_label}: ${b.score.toFixed(0)}/100">${icon}</span>`;
    }).join('')}</div>`;
}

function getAllGeneralBadges(results) {
    const badgeMap = new Map();

    Object.entries(generalTestBadgeMap).forEach(([key, meta]) => {
        badgeMap.set(key, {
            key,
            ...meta,
            scores: [],
            rating: 'none',
        });
    });

    results.forEach(r => {
        const category = r.prompt_category || 'general';
        const key = r.prompt_key || '';
        if (category !== 'general' || !badgeMap.has(key)) {
            return;
        }
        badgeMap.get(key).scores.push(Number(r.final_score || 0));
    });

    const badges = Array.from(badgeMap.values()).map(b => {
        let avgScore = 0;
        let rating = 'none';

        if (b.scores.length > 0) {
            avgScore = b.scores.reduce((sum, score) => sum + score, 0) / b.scores.length;
            if (avgScore >= 75) rating = 'good';
            else if (avgScore >= 45) rating = 'medium';
            else rating = 'bad';
        }

        return {
            ...b,
            score: avgScore,
            rating,
        };
    });

    return `<div class="general-badge-wrap">${badges.map(b => {
        return `<span class="general-badge general-badge-${b.rating}" title="${esc(b.label)}: ${b.rating === 'none' ? 'Not tested' : `${b.score.toFixed(0)}/100`}">
            <i class="${b.icon} general-badge-icon"></i>
        </span>`;
    }).join('')}</div>`;
}

function getAllEngineBadges(results) {
    const engineMap = new Map();

    Object.keys(engineSkillLabelMap).forEach(skill => {
        engineMap.set(skill, {
            engine_skill: skill,
            engine_skill_label: engineSkillLabelMap[skill],
            scores: [],
            rating: 'none'
        });
    });

    results.forEach(r => {
        if (r.engine_skill) {
            const skill = String(r.engine_skill).toLowerCase();
            const score = Number(r.engine_score || 0);

            if (engineMap.has(skill)) {
                engineMap.get(skill).scores.push(score);
            }
        }
    });

    const badges = Array.from(engineMap.values()).map(b => {
        let avgScore = 0;
        let rating = 'none';

        if (b.scores.length > 0) {
            avgScore = b.scores.reduce((sum, s) => sum + s, 0) / b.scores.length;
            if (avgScore >= 75) rating = 'good';
            else if (avgScore >= 45) rating = 'medium';
            else rating = 'bad';
        }

        return {
            ...b,
            score: avgScore,
            rating: rating
        };
    });

    return `<div class="engine-badge-wrap">${badges.map(b => {
        const iconClass = engineIconMap[b.engine_skill] || 'bi bi-gpu-card';
        return `<span class="engine-badge engine-badge-${b.rating}" title="${b.engine_skill_label}: ${b.score.toFixed(0)}/100">
            <i class="${iconClass} engine-badge-icon"></i>
        </span>`;
    }).join('')}</div>`;
}

function getAllSongwritingBadges(results) {
    const badges = Object.entries(songwritingCriterionMap).map(([key, meta]) => {
        const scores = results
            .filter(r => r.prompt_category === 'songwriting_tests' || Number(r.songwriting_score || 0) > 0)
            .map(r => Number(r[meta.field] || 0))
            .filter(score => score > 0);

        let avgScore = 0;
        let rating = 'none';
        if (scores.length > 0) {
            avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
            if (avgScore >= 75) rating = 'good';
            else if (avgScore >= 45) rating = 'medium';
            else rating = 'bad';
        }

        return {
            key,
            ...meta,
            score: avgScore,
            rating,
        };
    });

    return `<div class="song-badge-wrap">${badges.map(b => {
        return `<span class="song-badge song-badge-${b.rating}" title="${b.label}: ${songwritingRatingLabelMap[b.rating]} (${b.score.toFixed(0)}/100)">
            <i class="${b.icon} song-badge-icon"></i>
        </span>`;
    }).join('')}</div>`;
}

function getAllSongwritingPromptBadges(results) {
    const promptMap = new Map();

    Object.entries(songwritingPromptBadgeMap).forEach(([key, meta]) => {
        promptMap.set(key, {
            ...meta,
            scores: [],
            rating: 'none',
        });
    });

    results.forEach(r => {
        if (r.prompt_category !== 'songwriting_tests' && Number(r.songwriting_score || 0) <= 0) {
            return;
        }

        const key = r.prompt_key || '';
        const searchable = [
            key,
            r.prompt_name || '',
            r.songwriting_skill || '',
            r.songwriting_skill_label || '',
        ].join(' ').toLowerCase();

        Object.entries(songwritingPromptBadgeMap).forEach(([badgeKey, meta]) => {
            const isExactPrompt = key === badgeKey;
            const isLanguageFamily = Array.isArray(meta.match)
                && meta.match.some(term => searchable.includes(String(term).toLowerCase()));
            if (isExactPrompt || isLanguageFamily) {
                promptMap.get(badgeKey).scores.push(Number(r.songwriting_score || 0));
            }
        });
    });

    const badges = Array.from(promptMap.values()).map(b => {
        let avgScore = 0;
        let rating = 'none';
        if (b.scores.length > 0) {
            avgScore = b.scores.reduce((sum, score) => sum + score, 0) / b.scores.length;
            if (avgScore >= 75) rating = 'good';
            else if (avgScore >= 45) rating = 'medium';
            else rating = 'bad';
        }

        return {
            ...b,
            score: avgScore,
            rating,
        };
    });

    return `<div class="song-badge-wrap">${badges.map(b => {
        return `<span class="song-badge song-style-badge song-badge-${b.rating}" title="${esc(b.short)}: ${songwritingRatingLabelMap[b.rating]} (${b.score.toFixed(0)}/100)">
            ${esc(b.short)}
        </span>`;
    }).join('')}</div>`;
}

function capabilityBadges(results) {
    return `<div class="capability-badge-stack">
        ${getAllGeneralBadges(results)}
        ${getAllLanguageBadges(results)}
        ${getAllEngineBadges(results)}
        ${getAllSongwritingPromptBadges(results)}
        ${getAllSongwritingBadges(results)}
    </div>`;
}

// ── Load results ──

async function loadResults() {
    const tbody = document.getElementById('resultsBody');
    if (!tbody) return;
    
    try {
        const resp = await fetch('/api/results');
        const results = await resp.json();
        
        if (results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="14" class="text-center text-muted">No results available.</td></tr>';
            return;
        }
        
        const grouped = groupByModelName(results);
        grouped.sort((a, b) => (b.final_score || 0) - (a.final_score || 0));

        tbody.innerHTML = grouped.map((r, idx) => {
            const allResults = r._allResults || [r];
            return `
                <tr>
                    <td>${idx + 1}</td>
                    <td>${esc(r.model_name)}</td>
                    <td>${esc(r.prompt_name || '-')}</td>
                    <td>${capabilityBadges(allResults)}</td>
                    <td>${(r.generation_tokens_per_second || 0).toFixed(1)}</td>
                    <td>${formatElapsed(r.elapsed_seconds)}</td>
                    <td class="${scoreClass(r.quality_score)}">${(r.quality_score || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.format_score)}">${(r.format_score || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.consistency_score)}">${(r.consistency_score || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.stability_score)}">${(r.stability_score || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.final_score)}"><strong>${(r.final_score || 0).toFixed(1)}</strong></td>
                    <td>${r.self_validation_used ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-dash text-muted"></i>'}</td>
                    <td><span class="badge-status badge-${r.status}">${r.status}</span></td>
                    <td><small>${formatDate(r.created_at)}</small></td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteResult(${r.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="15" class="text-center text-danger">Error loading results.</td></tr>';
    }
}

// ── Load ranking ──

async function loadRanking() {
    const tbody = document.getElementById('rankingBody');
    if (!tbody) return;
    
    try {
        const resp = await fetch('/api/ranking');
        const results = await resp.json();
        
        if (results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="13" class="text-center text-muted">No results available.</td></tr>';
            return;
        }
        
        const grouped = groupByModelName(results);
        grouped.sort((a, b) => (b.final_score || 0) - (a.final_score || 0));
        
        const medals = ['🥇', '🥈', '🥉'];
        
        tbody.innerHTML = grouped.map((r, i) => {
            const place = i + 1;
            const medal = place <= 3 ? medals[place - 1] : `#${place}`;
            const rowClass = place <= 3 ? `ranking-place-${place}` : '';
            const finalScore = r.final_score != null ? r.final_score : 0;

            return `
                <tr class="${rowClass}">
                    <td><strong>${medal}</strong></td>
                    <td><strong>${esc(r.model_name)}</strong></td>
                    <td class="${scoreClass(finalScore)}"><strong>${finalScore.toFixed(1)}</strong></td>
                    <td>${(r.generation_tokens_per_second || 0).toFixed(1)}</td>
                    <td>${formatElapsed(r.elapsed_seconds)}</td>
                    <td>${(r.prompt_tokens_per_second || 0).toFixed(1)}</td>
                    <td>${(r.first_token_latency || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.quality_score)}">${(r.quality_score || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.format_score)}">${(r.format_score || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.consistency_score)}">${(r.consistency_score || 0).toFixed(1)}</td>
                    <td class="${scoreClass(r.stability_score)}">${(r.stability_score || 0).toFixed(1)}</td>
                    <td>${r.context_size ? r.context_size.toLocaleString('en-US') : '-'}</td>
                    <td><span class="badge-status badge-${r.status}">${r.status}</span></td>
                    <td><small>${formatDate(r.created_at)}</small></td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        console.error('Ranking error:', err);
        tbody.innerHTML = '<tr><td colspan="14" class="text-center text-danger">Error loading ranking.</td></tr>';
    }
}

// ── Delete result ──

// Detailed comparison page

let comparisonResults = [];
let comparisonResizeHandler = null;

async function loadComparisons() {
    const tableBody = document.getElementById('runComparisonBody');
    if (!tableBody) return;

    try {
        const resp = await fetch('/api/results');
        comparisonResults = await resp.json();

        buildComparisonFilters(comparisonResults);
        renderComparisons();

        if (!comparisonResizeHandler) {
            comparisonResizeHandler = debounce(renderComparisons, 150);
            window.addEventListener('resize', comparisonResizeHandler);
        }
    } catch (err) {
        console.error('Comparison error:', err);
        tableBody.innerHTML = '<tr><td colspan="9" class="text-center text-danger">Error loading comparisons.</td></tr>';
    }
}

function buildComparisonFilters(results) {
    const modelSelect = document.getElementById('comparisonModelFilter');
    const categorySelect = document.getElementById('comparisonCategoryFilter');
    if (!modelSelect || !categorySelect) return;

    const currentModel = modelSelect.value || 'all';
    const currentCategory = categorySelect.value || 'all';
    const models = uniqueSorted(results.map(r => r.model_name).filter(Boolean));
    const categories = uniqueSorted(results.map(r => normalizedCategory(r)).filter(Boolean));

    modelSelect.innerHTML = '<option value="all">All models</option>' + models
        .map(model => `<option value="${esc(model)}">${esc(model)}</option>`)
        .join('');
    categorySelect.innerHTML = '<option value="all">All categories</option>' + categories
        .map(category => `<option value="${esc(category)}">${esc(categoryLabel(category))}</option>`)
        .join('');

    modelSelect.value = models.includes(currentModel) ? currentModel : 'all';
    categorySelect.value = categories.includes(currentCategory) ? currentCategory : 'all';

    modelSelect.onchange = renderComparisons;
    categorySelect.onchange = renderComparisons;
}

function renderComparisons() {
    const modelFilter = document.getElementById('comparisonModelFilter')?.value || 'all';
    const categoryFilter = document.getElementById('comparisonCategoryFilter')?.value || 'all';

    const filtered = comparisonResults.filter(r => {
        if (modelFilter !== 'all' && r.model_name !== modelFilter) return false;
        if (categoryFilter !== 'all' && normalizedCategory(r) !== categoryFilter) return false;
        return true;
    });
    const scoreResults = filtered.filter(r => !isTruthAuditResult(r));
    const truthResults = filtered.filter(isTruthAuditResult);
    const runDeltas = buildRunDeltas(scoreResults);

    renderComparisonSummary(scoreResults, runDeltas);
    drawCategoryScoreCanvas('categoryScoreCanvas', scoreResults);
    drawSelfValidationCanvas('selfValidationCanvas', scoreResults);
    drawRunHistoryCanvas('runHistoryCanvas', scoreResults);
    drawTruthAuditCanvas('truthAuditCanvas', truthResults);
    renderRunComparisonTable(runDeltas);
}

function renderComparisonSummary(results, runDeltas) {
    setText('comparisonResultCount', results.length);
    setText('comparisonAvgScore', results.length ? avg(results, 'final_score').toFixed(1) : '-');

    const selfDeltas = results
        .map(r => selfValidationDelta(r))
        .filter(delta => delta !== null);
    const avgSelfDelta = selfDeltas.length
        ? selfDeltas.reduce((sum, delta) => sum + delta, 0) / selfDeltas.length
        : null;
    setText('comparisonAvgSelfDelta', avgSelfDelta === null ? '-' : formatSigned(avgSelfDelta));

    const better = runDeltas.filter(d => d.scoreDelta > 0).length;
    const worse = runDeltas.filter(d => d.scoreDelta < 0).length;
    setText('comparisonRunDeltaCount', runDeltas.length ? `${better} better / ${worse} worse` : '-');

    renderComparisonLeaders(results);
}

function renderComparisonLeaders(results) {
    const bestModel = bestModelByAverage(results, 'final_score', 'desc');
    const elapsedResults = results.filter(r => Number(r.elapsed_seconds) > 0);
    const fastestModel = bestModelByAverage(elapsedResults, 'elapsed_seconds', 'asc');
    const bestCodingModel = bestModelByGoodBadges(results);

    renderLeaderCard('comparisonBestModel', bestModel, {
        mainMetric: 'avg_score',
        mainLabel: 'avg score',
        secondaryMetric: 'test_count',
    });
    renderLeaderCardElapsed('comparisonFastestModel', fastestModel, {
        mainLabel: 'avg elapsed',
        secondaryMetric: 'avg_generation_tokens_per_second',
        secondaryLabel: 'avg tok/s',
    });
    renderBadgeLeaderCard('comparisonBestCodingModel', bestCodingModel);
}

// A badge (general test / programming language / engine skill) counts as
// 'good' when the model's average score across all its passes for that item
// is >= 75 - matching getAllGeneralBadges/getAllLanguageBadges/getAllEngineBadges.
function countGoodBadges(results) {
    const generalScores = new Map();
    const languageScores = new Map();
    const engineScores = new Map();

    results.forEach(r => {
        if (r.prompt_category === 'general' && r.prompt_key) {
            const key = r.prompt_key;
            if (!generalScores.has(key)) generalScores.set(key, []);
            generalScores.get(key).push(Number(r.final_score || 0));
        }
        if (r.programming_language) {
            const key = String(r.programming_language).toLowerCase();
            if (!languageScores.has(key)) languageScores.set(key, []);
            languageScores.get(key).push(Number(r.language_score || 0));
        }
        if (r.engine_skill) {
            const key = String(r.engine_skill).toLowerCase();
            if (!engineScores.has(key)) engineScores.set(key, []);
            engineScores.get(key).push(Number(r.engine_score || 0));
        }
    });

    const countGood = (map) => {
        let good = 0;
        map.forEach(scores => {
            const avgScore = scores.reduce((sum, v) => sum + v, 0) / scores.length;
            if (avgScore >= 75) good++;
        });
        return good;
    };

    const general = countGood(generalScores);
    const coding = countGood(languageScores);
    const engine = countGood(engineScores);
    return { general, coding, engine, total: general + coding + engine };
}

function bestModelByGoodBadges(results) {
    const groups = new Map();
    results.forEach(r => {
        const model = r.model_name || 'Unknown model';
        if (!groups.has(model)) groups.set(model, []);
        groups.get(model).push(r);
    });

    let best = null;
    groups.forEach((modelResults, model) => {
        const counts = countGoodBadges(modelResults);
        if (!best || counts.total > best.total_good_badges) {
            best = {
                model_name: model,
                total_good_badges: counts.total,
                general_badges: counts.general,
                coding_badges: counts.coding,
                engine_badges: counts.engine,
            };
        }
    });
    return best;
}

function renderBadgeLeaderCard(id, leader) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!leader) {
        el.innerHTML = '<div class="text-muted">No matching results.</div>';
        return;
    }

    const totalPossible = Object.keys(languageIconMap).length +
                         Object.keys(generalTestBadgeMap).length +
                         Object.keys(engineSkillLabelMap).length;

    el.innerHTML = `
        <div class="comparison-leader-name">${esc(leader.model_name)}</div>
        <div class="comparison-leader-metric">${leader.total_good_badges}/${totalPossible} <span>good badges</span></div>
        <div class="text-muted small">${leader.general_badges} general, ${leader.coding_badges} coding, ${leader.engine_badges} engine</div>
    `;
}

function bestModelByAverage(results, field, direction = 'desc') {
    if (!results.length) return null;
    const groups = new Map();
    results.forEach(r => {
        const model = r.model_name || 'Unknown model';
        if (!groups.has(model)) groups.set(model, []);
        groups.get(model).push(r);
    });

    const rows = Array.from(groups.entries()).map(([model, rows]) => ({
        model_name: model,
        test_count: rows.length,
        avg_score: avg(rows, 'final_score'),
        avg_generation_tokens_per_second: avg(rows, 'generation_tokens_per_second'),
        avg_total_duration: avg(rows, 'total_duration'),
        avg_elapsed_seconds: avg(rows, 'elapsed_seconds'),
        value: avg(rows, field),
    }));

    rows.sort((a, b) => direction === 'asc' ? a.value - b.value : b.value - a.value);
    return rows[0] || null;
}

function renderLeaderCard(id, leader, options) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!leader) {
        el.innerHTML = '<div class="text-muted">No matching results.</div>';
        return;
    }

    const mainValue = Number(leader[options.mainMetric] || 0).toFixed(1);
    const secondary = formatLeaderSecondary(leader, options);

    el.innerHTML = `
        <div class="comparison-leader-name">${esc(leader.model_name)}</div>
        <div class="comparison-leader-metric">${mainValue} <span>${esc(options.mainLabel)}</span></div>
        <div class="text-muted small">${secondary}</div>
    `;
}

function renderLeaderCardElapsed(id, leader, options) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!leader) {
        el.innerHTML = '<div class="text-muted">No matching results.</div>';
        return;
    }
    const elapsedVal = Number(leader.avg_elapsed_seconds || 0);
    const mainValue = formatElapsed(elapsedVal);
    const secondary = options.secondaryMetric && options.secondaryLabel
        ? `${Number(leader[options.secondaryMetric] || 0).toFixed(1)} ${options.secondaryLabel} (${leader.test_count} results)`
        : `${leader.test_count} result${leader.test_count === 1 ? '' : 's'}`;
    el.innerHTML = `
        <div class="comparison-leader-name">${esc(leader.model_name)}</div>
        <div class="comparison-leader-metric">${mainValue} <span>${esc(options.mainLabel)}</span></div>
        <div class="text-muted small">${secondary}</div>
    `;
}

function formatLeaderSecondary(leader, options) {
    if (options.secondaryMetric === 'test_count') {
        return `${leader.test_count} result${leader.test_count === 1 ? '' : 's'}`;
    }
    if (options.secondaryMetric && options.secondaryLabel) {
        return `${Number(leader[options.secondaryMetric] || 0).toFixed(1)} ${options.secondaryLabel} (${leader.test_count} results)`;
    }
    return `${leader.test_count} result${leader.test_count === 1 ? '' : 's'}`;
}

function drawCategoryScoreCanvas(canvasId, results) {
    const rows = buildBadgeScoreRows(results);
    setCanvasRowsHeight(canvasId, rows.length, 24, 360, 10000);

    drawHorizontalBars(canvasId, rows, {
        emptyText: 'No badge score data.',
        maxValue: 100,
    });
}

function buildBadgeScoreRows(results) {
    const entries = [];

    results.forEach(r => {
        const model = r.model_name || 'Unknown model';
        const category = normalizedCategory(r);
        const promptKey = r.prompt_key || '';

        if (category === 'general' && generalTestBadgeMap[promptKey]) {
            entries.push(makeBadgeScoreEntry(
                model,
                `General: ${generalTestBadgeMap[promptKey].short}`,
                Number(r.final_score || 0),
                'general'
            ));
        }

        if (r.programming_language && Number(r.language_score || 0) > 0) {
            entries.push(makeBadgeScoreEntry(
                model,
                `Language: ${r.programming_language_label || r.programming_language}`,
                Number(r.language_score || 0),
                'language'
            ));
        }

        if (r.engine_skill && Number(r.engine_score || 0) > 0) {
            entries.push(makeBadgeScoreEntry(
                model,
                `Engine: ${r.engine_skill_label || engineSkillLabelMap[r.engine_skill] || r.engine_skill}`,
                Number(r.engine_score || 0),
                'engine'
            ));
        }

        if ((category === 'songwriting_tests' || Number(r.songwriting_score || 0) > 0) && Number(r.songwriting_score || 0) > 0) {
            const promptBadge = songwritingPromptBadgeMap[promptKey];
            entries.push(makeBadgeScoreEntry(
                model,
                promptBadge ? `Song: ${promptBadge.label}` : `Song: ${r.prompt_name || r.songwriting_skill_label || 'Songwriting'}`,
                Number(r.songwriting_score || 0),
                'song'
            ));

            Object.values(songwritingCriterionMap).forEach(meta => {
                const score = Number(r[meta.field] || 0);
                if (score > 0) {
                    entries.push(makeBadgeScoreEntry(model, `Song Skill: ${meta.label}`, score, 'song-skill'));
                }
            });
        }
    });

    return aggregateBadgeScoreEntries(entries);
}

function makeBadgeScoreEntry(model, badge, score, type) {
    return {
        model,
        badge,
        score: clamp(score, 0, 100),
        type,
    };
}

function aggregateBadgeScoreEntries(entries) {
    const groups = new Map();
    entries.forEach(entry => {
        const key = `${entry.badge}::${entry.model}`;
        if (!groups.has(key)) {
            groups.set(key, {
                model: entry.model,
                badge: entry.badge,
                type: entry.type,
                scores: [],
            });
        }
        groups.get(key).scores.push(entry.score);
    });

    return Array.from(groups.values()).map(group => ({
        label: `${group.badge} - ${group.model}`,
        value: group.scores.reduce((sum, score) => sum + score, 0) / group.scores.length,
        badge: group.badge,
        model: group.model,
        type: group.type,
    })).map(row => ({
        ...row,
        color: badgeScoreColor(row.value),
    })).sort((a, b) => {
        const typeOrder = badgeTypeOrder(a.type) - badgeTypeOrder(b.type);
        if (typeOrder !== 0) return typeOrder;
        const badgeOrder = a.badge.localeCompare(b.badge);
        if (badgeOrder !== 0) return badgeOrder;
        return b.value - a.value;
    });
}

function badgeTypeOrder(type) {
    const order = {
        general: 1,
        language: 2,
        engine: 3,
        song: 4,
        'song-skill': 5,
    };
    return order[type] || 99;
}

function badgeScoreColor(score) {
    if (score <= 0) return '#4a5568';
    if (score >= 75) return '#20c997';
    if (score >= 45) return '#ffc107';
    return '#dc3545';
}

function drawSelfValidationCanvas(canvasId, results) {
    const rows = results
        .filter(r => Number(r.run1_quality_score || 0) > 0 && Number(r.run2_quality_score || 0) > 0)
        .sort((a, b) => Math.abs(selfValidationDelta(b) || 0) - Math.abs(selfValidationDelta(a) || 0));
    setCanvasRowsHeight(canvasId, rows.length, 42, 360, 10000);

    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;
    const { ctx, width, height } = canvas;
    clearCanvas(ctx, width, height);

    if (!rows.length) {
        drawEmpty(ctx, width, height, 'No self-validation pairs available.');
        return;
    }

    const pad = { left: 12, right: 12, top: 18, bottom: 18 };
    const plotW = width - pad.left - pad.right;
    const rowH = Math.max(42, (height - pad.top - pad.bottom) / rows.length);
    const labelW = Math.min(150, Math.max(100, plotW * 0.34));
    const valueW = Math.min(118, Math.max(92, plotW * 0.22));
    const gap = 10;
    const barX = pad.left + labelW;
    const barW = Math.max(80, plotW - labelW - valueW - gap);
    const blindColor = '#38bdf8';
    const selfColor = '#a78bfa';

    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillText('Prompt', pad.left, 11);
    ctx.fillText('0', barX, 11);
    ctx.fillText('50', barX + barW / 2 - 8, 11);
    ctx.fillText('100', barX + barW - 20, 11);

    ctx.strokeStyle = 'rgba(148, 163, 184, 0.18)';
    [0, 0.5, 1].forEach(pos => {
        const x = barX + barW * pos;
        ctx.beginPath();
        ctx.moveTo(x, pad.top - 4);
        ctx.lineTo(x, height - pad.bottom);
        ctx.stroke();
    });

    rows.forEach((r, idx) => {
        const rowTop = pad.top + idx * rowH;
        const y1 = rowTop + 12;
        const y2 = rowTop + 29;
        const barH = Math.min(10, Math.max(7, rowH * 0.22));
        const blind = clamp(Number(r.run1_quality_score || 0), 0, 100);
        const self = clamp(Number(r.run2_quality_score || 0), 0, 100);
        const delta = self - blind;
        const improved = delta > 0;
        const worse = delta < 0;
        const blindW = (blind / 100) * barW;
        const selfW = (self / 100) * barW;
        const deltaColor = improved ? '#22c55e' : worse ? '#ef4444' : '#94a3b8';

        ctx.fillStyle = '#94a3b8';
        ctx.font = `${rowH < 48 ? 10 : 11}px system-ui, sans-serif`;
        ctx.fillText(trimLabel(r.model_name || 'Unknown model', 18), pad.left, y1 + 3);
        ctx.fillStyle = '#f1f5f9';
        ctx.fillText(trimLabel(r.prompt_name || categoryLabel(normalizedCategory(r)), 20), pad.left, y2 + 3);

        drawSoftBar(ctx, barX, y1, barW, barH, 'rgba(56, 189, 248, 0.12)', '#30363d');
        drawSoftBar(ctx, barX, y2, barW, barH, 'rgba(167, 139, 250, 0.12)', '#30363d');
        drawSoftBar(ctx, barX, y1, blindW, barH, blindColor, blindColor);
        drawSoftBar(ctx, barX, y2, selfW, barH, selfColor, selfColor);

        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px system-ui, sans-serif';
        ctx.fillText(`Blind ${blind.toFixed(0)}`, barX + Math.min(blindW + 5, barW - 48), y1 + 8);
        ctx.fillText(`Self ${self.toFixed(0)}`, barX + Math.min(selfW + 5, barW - 42), y2 + 8);

        ctx.strokeStyle = deltaColor;
        ctx.lineWidth = 1.5;
        const arrowStart = barX + blindW;
        const arrowEnd = barX + selfW;
        const arrowY = rowTop + 24;
        drawDeltaArrow(ctx, arrowStart, arrowEnd, arrowY, deltaColor);

        ctx.fillStyle = deltaColor;
        ctx.font = `${width < 520 ? '700 10px' : '700 12px'} system-ui, sans-serif`;
        ctx.textAlign = 'right';
        const status = improved ? 'better' : worse ? 'worse' : 'same';
        ctx.fillText(`${formatSigned(delta)} ${status}`, width - pad.right, rowTop + 25);
        ctx.textAlign = 'left';
    });

    setCanvasTooltipRegions(canvas.canvas, rows.map((r, idx) => {
        const blind = Number(r.run1_quality_score || 0);
        const self = Number(r.run2_quality_score || 0);
        return {
            x: 0,
            y: pad.top + idx * rowH,
            w: width,
            h: rowH,
            title: `${r.model_name || 'Unknown model'}\n${r.prompt_name || categoryLabel(normalizedCategory(r))}\nBlind Analysis: ${blind.toFixed(1)}\nSelf-Validation: ${self.toFixed(1)}\nDelta: ${formatSigned(self - blind)}`,
        };
    }));
}

function drawRunHistoryCanvas(canvasId, results) {
    const series = buildRunHistorySeries(results)
        .sort((a, b) => b.points.length - a.points.length || b.latest - a.latest)
        .slice(0, 10);

    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;
    const { ctx, width, height } = canvas;
    clearCanvas(ctx, width, height);

    if (!series.length) {
        drawEmpty(ctx, width, height, 'Need at least two runs for the same model/category.');
        return;
    }

    const pad = { left: 42, right: 24, top: 24, bottom: 54 };
    const plotW = width - pad.left - pad.right;
    const plotH = height - pad.top - pad.bottom;
    drawAxis(ctx, pad.left, pad.top, plotW, plotH);

    series.forEach(s => {
        ctx.strokeStyle = s.color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        s.points.forEach((p, idx) => {
            const x = pad.left + (idx / Math.max(1, s.points.length - 1)) * plotW;
            const y = pad.top + plotH - (clamp(p.final_score, 0, 100) / 100) * plotH;
            if (idx === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        s.points.forEach((p, idx) => {
            const x = pad.left + (idx / Math.max(1, s.points.length - 1)) * plotW;
            const y = pad.top + plotH - (clamp(p.final_score, 0, 100) / 100) * plotH;
            ctx.fillStyle = s.color;
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, Math.PI * 2);
            ctx.fill();
        });
    });

    drawScaleLabels(ctx, pad.left, height - 28, plotW);
    drawInlineLegend(ctx, series.map(s => ({ label: s.label, color: s.color })), 12, height - 16, width - 24);
}

function drawTruthAuditCanvas(canvasId, results) {
    const rows = groupAverage(results, r => r.model_name || 'Unknown model', 'final_score')
        .map(g => ({ label: g.key, value: g.value, color: colorForString(g.key) }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 18);

    drawHorizontalBars(canvasId, rows, {
        emptyText: 'No Truth-Audit results found.',
        maxValue: 100,
    });
}

function renderRunComparisonTable(deltas) {
    const tbody = document.getElementById('runComparisonBody');
    if (!tbody) return;

    if (!deltas.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No repeated runs for the same model/category/prompt yet.</td></tr>';
        return;
    }

    tbody.innerHTML = deltas.slice(0, 120).map(d => {
        const status = d.scoreDelta > 0 ? 'better' : d.scoreDelta < 0 ? 'worse' : 'same';
        const statusClass = d.scoreDelta > 0 ? 'text-success' : d.scoreDelta < 0 ? 'text-danger' : 'text-muted';
        return `
            <tr>
                <td>${esc(d.current.model_name)}</td>
                <td>${esc(categoryLabel(normalizedCategory(d.current)))}</td>
                <td>${esc(d.current.prompt_name || d.current.prompt_key || '-')}</td>
                <td>${scoreCell(d.current.final_score)}</td>
                <td>${scoreCell(d.previous.final_score)}</td>
                <td class="${statusClass}"><strong>${formatSigned(d.scoreDelta)}</strong></td>
                <td class="${d.selfDelta === null ? 'text-muted' : d.selfDelta >= 0 ? 'text-success' : 'text-danger'}">${d.selfDelta === null ? '-' : formatSigned(d.selfDelta)}</td>
                <td class="${statusClass}">${status}</td>
                <td><small>${formatDate(d.current.created_at)}</small></td>
            </tr>
        `;
    }).join('');
}

function buildRunDeltas(results) {
    const groups = new Map();
    results.forEach(r => {
        const key = [
            r.model_name || '',
            normalizedCategory(r),
            r.prompt_key || r.prompt_name || '',
        ].join('::');
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(r);
    });

    const deltas = [];
    groups.forEach(items => {
        items.sort((a, b) => {
            const aTime = parseUtcDate(a.created_at)?.getTime() || 0;
            const bTime = parseUtcDate(b.created_at)?.getTime() || 0;
            if (aTime !== bTime) return aTime - bTime;
            return (a.id || 0) - (b.id || 0);
        });
        for (let i = 1; i < items.length; i += 1) {
            const current = items[i];
            const previous = items[i - 1];
            deltas.push({
                current,
                previous,
                scoreDelta: Number(current.final_score || 0) - Number(previous.final_score || 0),
                selfDelta: selfValidationDelta(current),
            });
        }
    });

    return deltas.sort((a, b) => {
        const aTime = parseUtcDate(a.current.created_at)?.getTime() || 0;
        const bTime = parseUtcDate(b.current.created_at)?.getTime() || 0;
        return bTime - aTime;
    });
}

function buildRunHistorySeries(results) {
    const groups = new Map();
    results.forEach(r => {
        const key = `${r.model_name || 'Unknown model'}::${normalizedCategory(r)}`;
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(r);
    });

    const series = [];
    groups.forEach((items, key) => {
        const points = groupAverageByRun(items);
        if (points.length < 2) return;
        const [model, category] = key.split('::');
        series.push({
            label: `${trimLabel(model, 16)} / ${categoryLabel(category)}`,
            color: colorForString(key),
            points,
            latest: points[points.length - 1].final_score,
        });
    });
    return series;
}

function groupAverageByRun(items) {
    const groups = new Map();
    items.forEach(r => {
        const key = r.run_id ? `run:${r.run_id}` : `row:${r.id}`;
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(r);
    });

    return Array.from(groups.values()).map(rows => {
        rows.sort((a, b) => (parseUtcDate(a.created_at)?.getTime() || 0) - (parseUtcDate(b.created_at)?.getTime() || 0));
        return {
            created_at: rows[0]?.created_at,
            final_score: avg(rows, 'final_score'),
        };
    }).sort((a, b) => (parseUtcDate(a.created_at)?.getTime() || 0) - (parseUtcDate(b.created_at)?.getTime() || 0));
}

function drawHorizontalBars(canvasId, rows, options = {}) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;
    const { ctx, width, height } = canvas;
    clearCanvas(ctx, width, height);

    if (!rows.length) {
        drawEmpty(ctx, width, height, options.emptyText || 'No data.');
        return;
    }

    const pad = { left: Math.min(260, Math.max(180, width * 0.32)), right: 46, top: 18, bottom: 30 };
    const plotW = width - pad.left - pad.right;
    const rowH = (height - pad.top - pad.bottom) / rows.length;
    const maxValue = options.maxValue || Math.max(1, ...rows.map(r => r.value));
    drawAxis(ctx, pad.left, pad.top, plotW, height - pad.top - pad.bottom);

    ctx.font = `${rowH < 14 ? 10 : 12}px system-ui, sans-serif`;
    rows.forEach((row, idx) => {
        const y = pad.top + idx * rowH + 3;
        const barH = Math.max(4, rowH - 7);
        const barW = (clamp(row.value, 0, maxValue) / maxValue) * plotW;

        ctx.fillStyle = '#94a3b8';
        ctx.fillText(trimLabel(row.label, Math.floor(pad.left / 7)), 12, y + barH - 1);
        ctx.fillStyle = row.color;
        ctx.fillRect(pad.left, y, barW, barH);
        ctx.fillStyle = '#f1f5f9';
        ctx.fillText(row.value.toFixed(1), pad.left + barW + 8, y + barH - 1);
    });

    drawScaleLabels(ctx, pad.left, height - 10, plotW);

    setCanvasTooltipRegions(canvas.canvas, rows.map((row, idx) => ({
        x: 0,
        y: pad.top + idx * rowH,
        w: width,
        h: rowH,
        title: row.model
            ? `${row.model}\n${row.badge || row.label}\nScore: ${row.value.toFixed(1)}`
            : `${row.label}\nScore: ${row.value.toFixed(1)}`,
    })));
}

function prepareCanvas(id) {
    const canvas = document.getElementById(id);
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const cssWidth = Math.max(320, Math.floor(rect.width || canvas.parentElement?.clientWidth || 640));
    const cssHeight = Number(canvas.getAttribute('height')) || 360;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.floor(cssWidth * ratio);
    canvas.height = Math.floor(cssHeight * ratio);
    canvas.style.width = `${cssWidth}px`;
    canvas.style.height = `${cssHeight}px`;
    const ctx = canvas.getContext('2d');
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { canvas, ctx, width: cssWidth, height: cssHeight };
}

function setCanvasRowsHeight(id, rowCount, rowHeight, minHeight, maxHeight) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const nextHeight = clamp(Math.ceil(rowCount * rowHeight + 54), minHeight, maxHeight);
    canvas.setAttribute('height', String(nextHeight));
}

function setCanvasTooltipRegions(canvas, regions) {
    canvas._tooltipRegions = regions || [];
    if (canvas._tooltipHandlerAttached) return;

    canvas.addEventListener('mousemove', function(event) {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const hit = (canvas._tooltipRegions || []).find(region =>
            x >= region.x && x <= region.x + region.w && y >= region.y && y <= region.y + region.h
        );
        canvas.title = hit ? hit.title : '';
    });

    canvas.addEventListener('mouseleave', function() {
        canvas.title = '';
    });

    canvas._tooltipHandlerAttached = true;
}

function clearCanvas(ctx, width, height) {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#0f1117';
    ctx.fillRect(0, 0, width, height);
}

function drawAxis(ctx, x, y, w, h) {
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, y + h);
    ctx.lineTo(x + w, y + h);
    ctx.stroke();

    for (let i = 1; i <= 4; i += 1) {
        const gx = x + (w / 4) * i;
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.16)';
        ctx.beginPath();
        ctx.moveTo(gx, y);
        ctx.lineTo(gx, y + h);
        ctx.stroke();
    }
}

function drawScaleLabels(ctx, x, y, w) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px system-ui, sans-serif';
    [0, 25, 50, 75, 100].forEach(value => {
        const px = x + (value / 100) * w;
        ctx.fillText(String(value), px - 7, y);
    });
}

function drawInlineLegend(ctx, items, x, y, maxWidth) {
    ctx.font = '11px system-ui, sans-serif';
    let cursorX = x;
    items.forEach(item => {
        const label = trimLabel(item.label, 18);
        const labelW = ctx.measureText(label).width + 24;
        if (cursorX + labelW > x + maxWidth) return;
        ctx.fillStyle = item.color;
        ctx.fillRect(cursorX, y - 8, 10, 10);
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(label, cursorX + 14, y);
        cursorX += labelW;
    });
}

function drawEmpty(ctx, width, height, text) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(text, width / 2, height / 2);
    ctx.textAlign = 'left';
}

function drawSoftBar(ctx, x, y, width, height, fill, stroke) {
    const radius = Math.min(4, height / 2);
    const w = Math.max(0, width);
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + w - radius, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
    ctx.lineTo(x + w, y + height - radius);
    ctx.quadraticCurveTo(x + w, y + height, x + w - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
    if (stroke) {
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 1;
        ctx.stroke();
    }
}

function drawDeltaArrow(ctx, startX, endX, y, color) {
    if (Math.abs(endX - startX) < 3) {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(startX, y, 2.5, 0, Math.PI * 2);
        ctx.fill();
        return;
    }

    const direction = endX > startX ? 1 : -1;
    const headSize = 5;
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(startX, y);
    ctx.lineTo(endX - direction * headSize, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(endX, y);
    ctx.lineTo(endX - direction * headSize, y - headSize * 0.7);
    ctx.lineTo(endX - direction * headSize, y + headSize * 0.7);
    ctx.closePath();
    ctx.fill();
}

function isTruthAuditResult(r) {
    const text = [
        r.prompt_category,
        r.prompt_key,
        r.prompt_name,
    ].join(' ').toLowerCase();
    return text.includes('truth_audit')
        || text.includes('truth-audit')
        || text.includes('truth audit');
}

function normalizedCategory(r) {
    return r.prompt_category || 'general';
}

function categoryLabel(category) {
    const map = {
        general: 'General',
        coding_language: 'Coding Language',
        game_engine: 'Game Engine',
        songwriting_tests: 'Songwriting',
        truth_audit: 'Truth-Audit',
    };
    return map[category] || String(category || 'General').replace(/_/g, ' ');
}

function selfValidationDelta(r) {
    const blind = Number(r.run1_quality_score || 0);
    const self = Number(r.run2_quality_score || 0);
    if (blind <= 0 || self <= 0) return null;
    return self - blind;
}

function groupAverage(items, keyFn, valueKey) {
    const groups = new Map();
    items.forEach(item => {
        const key = keyFn(item);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(Number(item[valueKey] || 0));
    });
    return Array.from(groups.entries()).map(([key, values]) => ({
        key,
        value: values.reduce((sum, value) => sum + value, 0) / values.length,
    }));
}

function avg(items, key) {
    if (!items.length) return 0;
    return items.reduce((sum, item) => sum + Number(item[key] || 0), 0) / items.length;
}

function uniqueSorted(values) {
    return Array.from(new Set(values)).sort((a, b) => String(a).localeCompare(String(b)));
}

function colorForString(value) {
    const colors = ['#38bdf8', '#22c55e', '#facc15', '#fb7185', '#a78bfa', '#f97316', '#2dd4bf', '#e879f9'];
    let hash = 0;
    String(value).split('').forEach(ch => {
        hash = ((hash << 5) - hash) + ch.charCodeAt(0);
        hash |= 0;
    });
    return colors[Math.abs(hash) % colors.length];
}

function trimLabel(label, maxLen) {
    const str = String(label || '');
    return str.length > maxLen ? `${str.slice(0, Math.max(0, maxLen - 1))}...` : str;
}

function formatSigned(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return '-';
    const num = Number(value);
    return `${num >= 0 ? '+' : ''}${num.toFixed(1)}`;
}

function scoreCell(value) {
    const score = Number(value || 0);
    return `<span class="${scoreClass(score)}">${score.toFixed(1)}</span>`;
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function debounce(fn, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), wait);
    };
}

async function deleteResult(id) {
    if (!confirm('Delete this result group? This also removes it from the ranking.')) return;
    
    try {
        const resp = await fetch(`/api/results/${id}`, { method: 'DELETE' });
        if (!resp.ok) {
            throw new Error('Delete failed.');
        }
        loadResults();
        loadRanking();
    } catch (err) {
        alert('Delete failed.');
    }
}

// ── Play sound ──

function playDoneSound() {
    try {
        // Try audio file
        const audio = new Audio('/static/sounds/done.mp3');
        audio.volume = 0.3;
        audio.play().catch(() => {
            // Fallback: browser oscillator
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            
            oscillator.frequency.value = 880;
            gainNode.gain.value = 0.1;
            
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 0.2);
        });
    } catch (err) {
        // No sound available
        console.debug('Sound not available:', err);
    }
}

// ── Show modal ──

function showDoneModal() {
    const modal = new bootstrap.Modal(document.getElementById('doneModal'));
    modal.show();
}

// ── Helper functions ──

function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        const d = parseUtcDate(dateStr);
        return d.toLocaleString('en-US', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    } catch {
        return dateStr;
    }
}

function parseUtcDate(dateStr) {
    if (!dateStr) return null;
    const normalized = dateStr.endsWith('Z') || dateStr.includes('+')
        ? dateStr
        : `${dateStr}Z`;
    const date = new Date(normalized);
    return Number.isNaN(date.getTime()) ? null : date;
}

function formatElapsed(seconds) {
    if (seconds == null || isNaN(seconds)) return '-';
    const total = Math.floor(Number(seconds));
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    const mm = String(m).padStart(2, '0');
    const ss = String(s).padStart(2, '0');
    return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

function formatStatus(status) {
    const map = {
        waiting: 'Waiting...',
        running: 'Running...',
        finished: 'Done!',
        failed: 'Error'
    };
    return map[status] || status;
}

function scoreClass(score) {
    if (!score) return '';
    if (score >= 50) return 'score-high';
    if (score >= 25) return 'score-medium';
    return 'score-low';
}

function startElapsedTimer() {
    const el = document.getElementById('elapsedTime');
    if (!el) return;

    if (window._elapsedInterval) {
        clearInterval(window._elapsedInterval);
    }
    
    const interval = setInterval(() => {
        const elapsed = Date.now() - benchmarkStartTime;
        const mins = Math.floor(elapsed / 60000);
        const secs = Math.floor((elapsed % 60000) / 1000);
        el.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }, 1000);
    
    // Interval is cleared on stop
    window._elapsedInterval = interval;
}

// ── Reset benchmark form for new run ──

function resetBenchmark() {
    forgetBenchmarkRun();
    document.getElementById('benchmarkForm').reset();
    
    document.getElementById('statusSpinner').className = 'spinner-border text-info me-3';
    document.getElementById('statusSpinner').innerHTML = '<span class="visually-hidden">Running...</span>';
    document.getElementById('statusTitle').textContent = 'Benchmark running...';
    document.getElementById('statusStep').textContent = '-';
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressBar').className = 'progress-bar progress-bar-striped progress-bar-animated bg-info';
    document.getElementById('progressPercent').textContent = '0%';
    document.getElementById('tokensPerSec').textContent = '-';
    document.getElementById('tokensPerSec').className = 'text-info';
    document.getElementById('decodedTokens').textContent = '-';
    document.getElementById('decodedTokens').className = '';
    document.getElementById('metricSource').textContent = '-';
    document.getElementById('metricSource').className = '';
    document.getElementById('elapsedTime').textContent = '00:00';
    
    document.getElementById('startBtn').disabled = false;
    document.getElementById('startBtn').innerHTML = '<i class="bi bi-play-fill"></i> Start Benchmark';
    document.getElementById('abortBtn').style.display = 'none';
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Helper: Group results by run_id ──
