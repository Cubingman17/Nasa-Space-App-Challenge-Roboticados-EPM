// DATA screen: the 5 NASA spaceflight hazards and how the astronaut is
// doing in each one, based on the metrics logged in Manual Data.

const DATA_API_URL = `${PYTHON_API_URL}/data`;

// The 5 NASA hazards and the catalog category that counts their records
const HAZARDS = {
    radiation: {
        title: "RADIATION",
        emoji: "☢️",
        color: "#f43f5e",
        catalog: "radiation",
        description: "Space ionizing radiation: chromosomal aberrations and cumulative dose measured by onboard dosimetry."
    },
    isolation: {
        title: "ISOLATION & CONFINEMENT",
        emoji: "🚪",
        color: "#8b5cf6",
        catalog: "psychology",
        description: "Confinement in a closed habitat degrades mood, sleep and raises chronic fatigue."
    },
    gravity: {
        title: "ALTERED GRAVITY",
        emoji: "🦴",
        color: "#fbbf24",
        catalog: "microgravity",
        description: "Microgravity causes bone mineral density loss, muscle atrophy and cardiovascular deconditioning."
    },
    environment: {
        title: "HOSTILE ENVIRONMENT",
        emoji: "🏭",
        color: "#10b981",
        catalog: "environment",
        description: "A closed environment can turn hostile fast: cabin CO2, oxygen, pressure and temperature must stay nominal."
    },
    distance: {
        title: "DISTANCE & BEHAVIORAL HEALTH",
        emoji: "🛰️",
        color: "#0ea5e9",
        catalog: "psychology",
        description: "Far from Earth there is no real-time ground support: psychomotor vigilance (PVT) and sleep mark the behavioral risk."
    }
};

// Metrics from the astronaut's last reading that feed each hazard
const HAZARD_METRICS = {
    radiation: [
        { key: "radiation", label: "Radiation dose", why: "Daily µSv exposure measured by onboard dosimetry." }
    ],
    isolation: [
        { key: "mood", label: "Mood index", why: "Self-reported well-being declines with confinement." },
        { key: "fatigue", label: "Fatigue level", why: "Confinement and monotony raise chronic fatigue." },
        { key: "sleep", label: "Sleep hours", why: "Sleep quality degrades in isolated habitats." }
    ],
    gravity: [
        { key: "bpm", label: "Heart rate", why: "Cardiovascular deconditioning in microgravity shows as resting heart rate drift." },
        { key: "blood_pressure", label: "Blood pressure", why: "Orthostatic intolerance: blood pressure control degrades without gravity." }
    ],
    environment: [
        { key: "cabin_co2", label: "Cabin CO2", why: "CO2 buildup in a closed environment impairs cognition." },
        { key: "body_temp", label: "Body temperature", why: "Thermal regulation stress in a hostile cabin." },
        { key: "spO2", label: "Blood oxygen (SpO2)", why: "Oxygen saturation reflects life-support performance." }
    ],
    distance: [
        { key: "reaction", label: "PVT reaction time", why: "The gold-standard behavioral health marker for fatigue." },
        { key: "sleep", label: "Sleep hours", why: "Sleep loss is the main driver of behavioral risk far from Earth." },
        { key: "fatigue", label: "Fatigue level", why: "Accumulated fatigue on long-distance missions." }
    ]
};

async function requestDataApi(path) {
    const response = await fetch(`${DATA_API_URL}${path}`);
    if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `Data API request failed (${response.status})`);
    }
    return response.json();
}

// The DATA tables must only show the selected astronaut's own real
// records, never the synthetic CSV dataset rows.
function currentSubjectId() {
    const subject = typeof getSelectedSubject === "function" ? getSelectedSubject() : null;
    return String(subject || "A");
}

function withSubject(path) {
    return `${path}${path.includes("?") ? "&" : "?"}astronaut_id=${encodeURIComponent(currentSubjectId())}`;
}

// Fill the "N records logged" line of each hazard card
async function loadDataCategories() {
    try {
        const payload = await requestDataApi(withSubject(""));
        const byCategory = {};
        for (const category of payload.categories || []) {
            byCategory[category.id] = category;
        }
        for (const [hazardId, hazard] of Object.entries(HAZARDS)) {
            const count = document.getElementById(`category-count-${hazardId}`);
            const category = byCategory[hazard.catalog];
            if (count) {
                count.textContent = category
                    ? (category.observation_count
                        ? `${category.observation_count} records logged`
                        : "no records logged yet")
                    : "No catalog data";
            }
        }
    } catch (error) {
        Object.keys(HAZARDS).forEach((hazardId) => {
            const count = document.getElementById(`category-count-${hazardId}`);
            if (count) count.textContent = "Data service unavailable";
        });
    }
}

// Severity of a status string: 'normal: nervous/stressed' counts as 'normal'
function severityOf(status) {
    const order = { normal: 0, atention: 1, bad: 2, critical: 3 };
    return order[String(status || "").split(":")[0].trim()] ?? -1;
}

// Hazard status = the most severe metric logged for that hazard.
// Returns null when nothing has been logged (no fake defaults).
function computeHazardStatus(hazardId, metrics) {
    let worst = null;
    for (const entry of HAZARD_METRICS[hazardId] || []) {
        const metric = metrics[entry.key];
        if (!metric) continue;
        const base = String(metric.status).split(":")[0].trim();
        if (worst === null || severityOf(base) > severityOf(worst)) {
            worst = base;
        }
    }
    return worst;
}

// Per hazard: its calculated status plus the metrics that determine it,
// with how each one is doing right now
function renderHazardMetrics(hazardId) {
    const container = document.getElementById("detail-metrics");
    if (!container) return;

    const subject = typeof getSelectedSubject === "function" ? getSelectedSubject() : "A";
    const reading = typeof getLastReading === "function" ? getLastReading(subject) : null;
    const metrics = reading ? (reading.metrics || {}) : {};

    const hazardStatus = computeHazardStatus(hazardId, metrics);
    const pillClass = {
        NORMAL: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
        ATENTION: "bg-amber-500/20 text-amber-300 border-amber-500/40",
        BAD: "bg-orange-500/20 text-orange-300 border-orange-500/40",
        CRITICAL: "bg-rose-500/20 text-rose-300 border-rose-500/40"
    }[hazardStatus ? hazardStatus.toUpperCase() : ""];
    const statusPill = hazardStatus
        ? `<span class="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${pillClass}">HAZARD STATUS: ${hazardStatus.toUpperCase()}</span>`
        : `<span class="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border bg-slate-800 text-slate-400 border-slate-600">HAZARD STATUS: NO DATA</span>`;

    let rows = "";
    for (const entry of HAZARD_METRICS[hazardId] || []) {
        const metric = metrics[entry.key];
        const color = metric ? statusColor(metric.status) : "#64748b";
        const value = metric
            ? `${escapeHtml(String(metric.value))}${escapeHtml(metric.unit)} — ${escapeHtml(metric.status)}`
            : "not logged yet";
        rows += `<div class="flex items-start gap-2 py-1 border-b border-slate-800 last:border-0">
            <span class="w-2.5 h-2.5 rounded-full mt-1 shrink-0" style="background:${color}"></span>
            <div>
                <p class="font-bold text-slate-200 text-[11px]">${escapeHtml(entry.label)}: <span class="font-normal text-slate-400">${value}</span></p>
                <p class="text-[10px] text-slate-500 leading-snug">${escapeHtml(entry.why)}</p>
            </div>
        </div>`;
    }

    container.innerHTML = `
        <div class="flex items-center gap-2 flex-wrap">
            <p class="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">How is this hazard:</p>
            ${statusPill}
        </div>
        <p class="text-[10px] font-extrabold uppercase tracking-widest text-slate-400 mt-2 mb-1">Metrics that feed this hazard</p>
        ${rows}
    `;
}

async function openRiskDetail(hazardId) {
    const hazard = HAZARDS[hazardId];
    if (!hazard) return;

    document.getElementById("data-overview").classList.add("hidden");
    document.getElementById("data-detail-view").classList.remove("hidden");
    document.getElementById("btn-back-data").classList.remove("hidden");

    const title = document.getElementById("detail-title");
    const description = document.getElementById("detail-description");
    const status = document.getElementById("dataset-load-status");

    title.textContent = `${hazard.emoji} ${hazard.title}`;
    description.textContent = hazard.description;
    status.textContent = "Loading…";
    renderHazardMetrics(hazardId);

    try {
        const category = await requestDataApi(withSubject(`/${encodeURIComponent(hazard.catalog)}`));
        status.textContent = category.observation_count
            ? `${category.observation_count} records logged by this astronaut`
            : "No records logged yet — use ➕ Log Manual Data";
    } catch (error) {
        status.textContent = "Records count unavailable (backend offline).";
    }
}

function closeRiskDetail() {
    document.getElementById("data-detail-view").classList.add("hidden");
    document.getElementById("btn-back-data").classList.add("hidden");
    document.getElementById("data-overview").classList.remove("hidden");
}

// -------------------------------------------------------------------------
// Status dots per hazard + OVERALL panel (separate from individual hazards)
// -------------------------------------------------------------------------
function updateHazardDots() {
    const subject = typeof getSelectedSubject === "function" ? getSelectedSubject() : "A";
    const reading = typeof getLastReading === "function" ? getLastReading(subject) : null;
    const metrics = reading ? (reading.metrics || {}) : {};

    // One dot per hazard, computed from its own logged metrics.
    // Gray = nothing logged yet for that hazard (no fake defaults).
    for (const hazardId of Object.keys(HAZARDS)) {
        const dot = document.getElementById(`py-dot-${hazardId}`);
        if (!dot) continue;
        const status = computeHazardStatus(hazardId, metrics);
        if (status) {
            dot.style.background = statusColor(status);
            dot.title = `Hazard status: ${status}`;
        } else {
            dot.style.background = "#64748b";
            dot.title = "No data logged for this hazard yet";
        }
    }

    // Overall panel: the general hazard, separate from the individual ones
    const pill = document.getElementById("py-overall-pill");
    if (pill) {
        if (reading) {
            const overall = String(reading.overall_status || "normal").split(":")[0].trim().toUpperCase();
            const pillClass = {
                NORMAL: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
                ATENTION: "bg-amber-500/20 text-amber-300 border-amber-500/40",
                BAD: "bg-orange-500/20 text-orange-300 border-orange-500/40",
                CRITICAL: "bg-rose-500/20 text-rose-300 border-rose-500/40"
            }[overall] || "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
            pill.innerText = overall;
            pill.className = "text-xs font-extrabold px-3 py-1 rounded-full border " + pillClass;
        } else {
            pill.innerText = "NO DATA";
            pill.className = "text-xs font-extrabold px-3 py-1 rounded-full border bg-slate-800 text-slate-400 border-slate-600";
        }
    }
}

// -------------------------------------------------------------------------
// Manual data entry modal (injected once, shared by DATA and HOME)
// -------------------------------------------------------------------------
const MANUAL_MODAL_HTML = `
<div id="manual-data-modal" class="hidden absolute inset-0 z-30 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-3">
    <div class="ui-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-5 shadow-2xl border-blue-500/40 flex flex-col gap-4">

        <div class="flex items-center justify-between border-b-2 border-blue-500/40 pb-3">
            <div>
                <h3 class="font-extrabold text-base uppercase tracking-wide text-blue-400">📡 Log Your Metrics</h3>
                <p class="text-[11px] text-slate-400">Fields marked with <span class="text-rose-300 font-bold">*</span> are required. The rest are optional.</p>
            </div>
            <button onclick="toggleManualModal(false)" class="text-slate-400 hover:text-white font-bold text-lg px-2">✕</button>
        </div>

        <div>
            <h4 class="text-[10px] font-extrabold uppercase tracking-widest text-rose-300 mb-2 flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span> Required
            </h4>
            <div class="space-y-2">
                <div class="flex items-center gap-3 bg-slate-900/80 border-l-4 border-rose-500/70 rounded-xl px-3 py-2">
                    <span class="text-lg shrink-0">💓</span>
                    <div class="flex-1 min-w-0"><p class="text-xs font-bold text-slate-200">BPM (Heart Rate) <span class="text-rose-300">*</span></p><p class="text-[10px] text-slate-500">60-100 bpm is optimal</p></div>
                    <input type="number" min="20" max="250" id="py-input-lpm" placeholder="68" class="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-bold text-sm text-right">
                </div>
                <div class="flex items-center gap-3 bg-slate-900/80 border-l-4 border-rose-500/70 rounded-xl px-3 py-2">
                    <span class="text-lg shrink-0">🫁</span>
                    <div class="flex-1 min-w-0"><p class="text-xs font-bold text-slate-200">SpO2 <span class="text-rose-300">*</span></p><p class="text-[10px] text-slate-500">≥ 95% is optimal</p></div>
                    <input type="number" min="50" max="100" id="py-input-spo2" placeholder="98" class="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-bold text-sm text-right">
                </div>
                <div class="flex items-center gap-3 bg-slate-900/80 border-l-4 border-rose-500/70 rounded-xl px-3 py-2">
                    <span class="text-lg shrink-0">😴</span>
                    <div class="flex-1 min-w-0"><p class="text-xs font-bold text-slate-200">Sleep (hours) <span class="text-rose-300">*</span></p><p class="text-[10px] text-slate-500">≥ 8 h is optimal</p></div>
                    <input type="number" min="0" max="24" step="0.1" id="py-input-sleep" placeholder="7.5" class="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-bold text-sm text-right">
                </div>
                <div class="flex items-center gap-3 bg-slate-900/80 border-l-4 border-rose-500/70 rounded-xl px-3 py-2">
                    <span class="text-lg shrink-0">⚡</span>
                    <div class="flex-1 min-w-0"><p class="text-xs font-bold text-slate-200">Reaction time (ms) <span class="text-rose-300">*</span></p><p class="text-[10px] text-slate-500">≤ 250 ms is optimal (PVT)</p></div>
                    <input type="number" min="50" max="2000" id="py-input-rt" placeholder="240" class="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-bold text-sm text-right">
                </div>
                <div class="flex items-center gap-3 bg-slate-900/80 border-l-4 border-rose-500/70 rounded-xl px-3 py-2">
                    <span class="text-lg shrink-0">🧠</span>
                    <div class="flex-1 min-w-0"><p class="text-xs font-bold text-slate-200">Fatigue (1-10) <span class="text-rose-300">*</span></p><p class="text-[10px] text-slate-500">≤ 3 is optimal</p></div>
                    <input type="number" min="1" max="10" id="py-input-fatigue" placeholder="3" class="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-bold text-sm text-right">
                </div>
            </div>
        </div>

        <div>
            <h4 class="text-[10px] font-extrabold uppercase tracking-widest text-slate-400 mb-2 flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-slate-500"></span> Optional
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">🩸</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Glucose (mg/dL)</p>
                    <input type="number" min="20" max="600" id="py-input-glucose" placeholder="95" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">🩺</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">BP systolic (mmHg)</p>
                    <input type="number" min="40" max="250" id="py-input-bp-sys" placeholder="120" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">🩺</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">BP diastolic (mmHg)</p>
                    <input type="number" min="40" max="250" id="py-input-bp-dia" placeholder="80" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">🌡️</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Body temp (°C)</p>
                    <input type="number" min="30" max="45" step="0.1" id="py-input-body-temp" placeholder="36.6" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">😊</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Mood (1-10)</p>
                    <input type="number" min="1" max="10" id="py-input-mood" placeholder="8" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">☢️</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Radiation (µSv/day)</p>
                    <input type="number" min="0" max="100000" id="py-input-rad" placeholder="400" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">💨</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Cabin CO2 (ppm)</p>
                    <input type="number" min="100" max="20000" id="py-input-co2" placeholder="900" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">🌡️</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Cabin temp (°C)</p>
                    <input type="number" min="-20" max="60" step="0.1" id="py-input-temp" placeholder="22.5" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">⚖️</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Weight (kg)</p>
                    <input type="number" min="20" max="300" step="0.1" id="py-input-weight" placeholder="70.5" class="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white font-bold text-xs text-right">
                </div>
                <div class="flex items-center gap-2 bg-slate-900/60 border-l-4 border-slate-600 rounded-xl px-3 py-1.5">
                    <span class="text-sm shrink-0">📝</span>
                    <p class="flex-1 text-[11px] font-bold text-slate-300">Session notes</p>
                    <input type="text" id="py-input-notes" placeholder="E.g. after exercise" class="w-32 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-white text-xs">
                </div>
            </div>
        </div>

        <div id="modal-feedback" class="hidden text-xs font-semibold p-3 rounded-xl border"></div>

        <div class="flex justify-end gap-3 pt-1">
            <button onclick="toggleManualModal(false)" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold">Cancel</button>
            <button id="py-submit-sensors" onclick="submitManualSensors()" class="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-extrabold uppercase tracking-wider shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
                📤 Analyze my data
            </button>
        </div>
    </div>
</div>`;

function ensureManualModal() {
    if (!document.getElementById("manual-data-modal")) {
        const wrapper = document.createElement("div");
        wrapper.innerHTML = MANUAL_MODAL_HTML;
        document.body.appendChild(wrapper.firstElementChild);
    }
}

function toggleManualModal(show) {
    ensureManualModal();
    const modal = document.getElementById("manual-data-modal");
    const feedback = document.getElementById("modal-feedback");
    if (show) {
        modal.classList.remove("hidden");
        feedback.classList.add("hidden");
    } else {
        modal.classList.add("hidden");
    }
}

// Optional inputs: only sent when the user filled them in.
const OPTIONAL_INPUTS = {
    blood_glucose: "py-input-glucose",
    bp_systolic: "py-input-bp-sys",
    bp_diastolic: "py-input-bp-dia",
    body_temp_c: "py-input-body-temp",
    mood_level: "py-input-mood",
    radiation_usv: "py-input-rad",
    cabin_co2: "py-input-co2",
    env_temp: "py-input-temp",
    weight_kg: "py-input-weight"
};

// Sane ranges: values outside these are rejected (e.g. BPM of 1e32)
const VALUE_RANGES = {
    hr_bpm: [20, 250, "BPM (20-250)"],
    spo2_pct: [50, 100, "SpO2 (50-100%)"],
    sleep_hours: [0, 24, "Sleep (0-24 h)"],
    rt_ms: [50, 2000, "Reaction (50-2000 ms)"],
    fatigue_level: [1, 10, "Fatigue (1-10)"],
    blood_glucose: [20, 600, "Glucose (20-600 mg/dL)"],
    bp_systolic: [40, 250, "BP systolic (40-250 mmHg)"],
    bp_diastolic: [40, 250, "BP diastolic (40-250 mmHg)"],
    body_temp_c: [30, 45, "Body temp (30-45 °C)"],
    mood_level: [1, 10, "Mood (1-10)"],
    radiation_usv: [0, 100000, "Radiation (0-100000 µSv)"],
    cabin_co2: [100, 20000, "Cabin CO2 (100-20000 ppm)"],
    weight_kg: [20, 300, "Weight (20-300 kg)"]
};

function validateRanges(payload) {
    const invalid = [];
    for (const [field, [min, max, label]] of Object.entries(VALUE_RANGES)) {
        const value = parseFloat(payload[field]);
        if (!isNaN(value) && (value < min || value > max)) invalid.push(label);
    }
    return invalid;
}

// Feedback styles by overall status severity
const STATUS_STYLES = {
    normal: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
    atention: "text-amber-300 bg-amber-500/10 border-amber-500/30",
    bad: "text-orange-300 bg-orange-500/10 border-orange-500/30",
    critical: "text-rose-300 bg-rose-500/10 border-rose-500/30"
};

// Structured, easy-to-read feedback: status pill + suggestion list
function renderFeedback(feedback, overall, suggestions, extraLine) {
    const overallUpper = overall.toUpperCase();
    const pillClass = {
        NORMAL: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
        ATENTION: "bg-amber-500/20 text-amber-300 border-amber-500/40",
        BAD: "bg-orange-500/20 text-orange-300 border-orange-500/40",
        CRITICAL: "bg-rose-500/20 text-rose-300 border-rose-500/40"
    }[overallUpper] || "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";

    let html = `<div class="flex items-center gap-2 mb-1.5">
        <span class="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${pillClass}">OVERALL: ${overallUpper}</span>
        ${extraLine ? `<span class="text-emerald-300 font-bold">${escapeHtml(extraLine)}</span>` : ""}
    </div>`;

    if (suggestions && suggestions.length) {
        html += `<p class="text-[10px] font-bold uppercase text-slate-400 mb-1">How to improve:</p><ul class="space-y-1">`;
        suggestions.forEach(tip => {
            html += `<li class="flex items-start gap-1.5"><span class="text-amber-400 mt-0.5">▸</span><span>${escapeHtml(tip)}</span></li>`;
        });
        html += `</ul>`;
    } else {
        html += `<p>All metrics in optimal range. Keep it up! 🚀</p>`;
    }

    feedback.className = "text-xs font-semibold p-3 rounded-xl border " + (STATUS_STYLES[overall] || STATUS_STYLES.normal);
    feedback.innerHTML = html;
}

async function submitManualSensors() {
    const payload = {
        subject_id: typeof getSelectedSubject === "function"
            ? getSelectedSubject()
            : (localStorage.getItem("selectedSubject") || "A"),
        hr_bpm: document.getElementById("py-input-lpm").value,
        spo2_pct: document.getElementById("py-input-spo2").value,
        sleep_hours: document.getElementById("py-input-sleep").value,
        rt_ms: document.getElementById("py-input-rt").value,
        fatigue_level: document.getElementById("py-input-fatigue").value,
        notes: document.getElementById("py-input-notes").value
    };

    for (const [field, inputId] of Object.entries(OPTIONAL_INPUTS)) {
        const value = document.getElementById(inputId).value;
        if (value !== "") payload[field] = value;
    }

    const feedback = document.getElementById("modal-feedback");
    const submitBtn = document.getElementById("py-submit-sensors");
    feedback.classList.remove("hidden");

    if (!payload.hr_bpm || !payload.spo2_pct || !payload.sleep_hours || !payload.rt_ms || !payload.fatigue_level) {
        feedback.className = "text-xs font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-xl text-center";
        feedback.innerText = "⚠️ Complete all required fields: BPM, SpO2, Sleep, Reaction and Fatigue.";
        return;
    }

    const invalid = validateRanges(payload);
    if (invalid.length) {
        feedback.className = "text-xs font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-xl text-center";
        feedback.innerText = `⚠️ Values out of range: ${invalid.join(", ")}.`;
        return;
    }

    submitBtn.disabled = true;
    feedback.className = "text-xs font-semibold text-sky-300 bg-sky-500/10 border border-sky-500/30 p-2.5 rounded-xl text-center";
    feedback.innerText = "📡 Analyzing your metrics...";

    const response = await PythonBridge.sendSensorData(payload);

    submitBtn.disabled = false;

    // Backend offline: warn and do NOT fake a healthy state
    if (response.offline || !response.overall_status) {
        feedback.className = "text-xs font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-xl text-center";
        feedback.innerText = response.ai_response;
        return;
    }

    // Save the subject's state for the console border and the AI banners
    const overall = String(response.overall_status || "normal").split(":")[0].trim();
    try {
        localStorage.setItem(`lastOverallStatus_${payload.subject_id}`, overall);
        localStorage.setItem(`lastAiResponse_${payload.subject_id}`, response.ai_response || "");
        localStorage.setItem(`lastReading_${payload.subject_id}`, JSON.stringify(response));
    } catch (error) {
        // localStorage unavailable: continue without persisting
    }
    if (typeof applyHealthState === "function") applyHealthState(overall);
    updateHazardDots();
    loadDataCategories();

    // Gamification: XP, points and streak for this astronaut
    let extraLine = "";
    if (typeof updateProfileProgress === "function") {
        const result = updateProfileProgress(payload.subject_id, payload, response);
        if (result) extraLine = `+${result.earned} pts earned!`;
    }

    renderFeedback(feedback, overall, response.suggestions, extraLine);

    setTimeout(() => {
        toggleManualModal(false);
        resetManualForm();
    }, 6000);
}

function resetManualForm() {
    ["py-input-lpm", "py-input-spo2", "py-input-sleep", "py-input-rt",
     "py-input-fatigue", "py-input-glucose", "py-input-bp-sys", "py-input-bp-dia",
     "py-input-body-temp", "py-input-mood", "py-input-rad", "py-input-co2",
     "py-input-temp", "py-input-weight", "py-input-notes"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    ensureManualModal();
    updateHazardDots();
    loadDataCategories();
});
