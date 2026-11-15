let detailChartInstance = null;

// The 5 NASA spaceflight hazards: radiation, isolation, altered gravity,
// hostile environment, and distance (behavioral health).
const risksDatabase = {
    radiation: {
        title: "RADIATION & BIODOSIMETRY",
        badge: "NASA LSDA Dataset",
        description: "Assessment of chromosomal aberrations induced by space ionizing radiation.",
        pre: "2.4 c/cell",
        inFlight: "8.9 c/cell",
        post: "8.2 c/cell",
        chartColor: "#f43f5e",
        bgTint: "rgba(244, 63, 94, 0.12)",
        borderTint: "rgba(244, 63, 94, 0.5)",
        dataValues: [2.4, 8.9, 8.2]
    },
    isolation: {
        title: "ISOLATION & CONFINEMENT",
        badge: "Crew Self-Reports (n=3)",
        description: "Decline in mood and rising fatigue caused by prolonged isolation and confinement inside a closed habitat.",
        pre: "8.1 /10",
        inFlight: "5.6 /10",
        post: "7.2 /10",
        chartColor: "#8b5cf6",
        bgTint: "rgba(139, 92, 246, 0.12)",
        borderTint: "rgba(139, 92, 246, 0.5)",
        dataValues: [8.1, 5.6, 7.2]
    },
    gravity: {
        title: "GRAVITY (Bone Mineral Density)",
        badge: "NASA OSDR Dataset",
        description: "Bone mass loss in hip and spine caused by prolonged microgravity exposure.",
        pre: "1.18 g/cm²",
        inFlight: "1.09 g/cm²",
        post: "1.11 g/cm²",
        chartColor: "#fbbf24",
        bgTint: "rgba(251, 191, 36, 0.12)",
        borderTint: "rgba(251, 191, 36, 0.5)",
        dataValues: [1.18, 1.09, 1.11]
    },
    environment: {
        title: "HOSTILE ENVIRONMENT (Cabin / Analog)",
        badge: "Environmental Control",
        description: "Stability of cabin CO2, ambient oxygen levels, pressure and controlled test conditions on Earth.",
        pre: "99% Nominal",
        inFlight: "98% Nominal",
        post: "99% Nominal",
        chartColor: "#10b981",
        bgTint: "rgba(16, 185, 129, 0.12)",
        borderTint: "rgba(16, 185, 129, 0.5)",
        dataValues: [99, 98, 99]
    },
    distance: {
        title: "DISTANCE & BEHAVIORAL HEALTH (PVT)",
        badge: "Part 1 Model (n=3)",
        description: "Increase in reaction times (>500 ms = lapse) associated with sleep deprivation and the behavioral load of deep-space operations.",
        pre: "235 ms",
        inFlight: "410 ms",
        post: "260 ms",
        chartColor: "#0ea5e9",
        bgTint: "rgba(14, 165, 233, 0.12)",
        borderTint: "rgba(14, 165, 233, 0.5)",
        dataValues: [235, 410, 260]
    }
};

function openRiskDetail(riskKey) {
    const info = risksDatabase[riskKey];
    if (!info) return;

    document.getElementById("data-overview").classList.add("hidden");
    document.getElementById("data-detail-view").classList.remove("hidden");
    document.getElementById("btn-back-data").classList.remove("hidden");

    document.getElementById("detail-badge").innerText = info.badge;
    document.getElementById("detail-title").innerText = info.title;
    document.getElementById("detail-description").innerText = info.description;
    document.getElementById("stat-pre").innerText = info.pre;
    document.getElementById("stat-in").innerText = info.inFlight;
    document.getElementById("stat-post").innerText = info.post;

    const chartContainer = document.getElementById("detail-chart-container");
    chartContainer.style.backgroundColor = info.bgTint;
    chartContainer.style.borderColor = info.borderTint;

    const ctx = document.getElementById("riskDetailChart").getContext("2d");
    if (detailChartInstance) detailChartInstance.destroy();

    detailChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Pre-Flight", "In-Flight", "Post-Flight"],
            datasets: [{
                label: info.title,
                data: info.dataValues,
                backgroundColor: [info.chartColor, "#3b82f6", "#8b5cf6"],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: "rgba(255,255,255,0.08)" }, ticks: { color: "#cbd5e1" } },
                x: { grid: { display: false }, ticks: { color: "#cbd5e1", font: { weight: "bold" } } }
            }
        }
    });
}

function closeRiskDetail() {
    document.getElementById("data-detail-view").classList.add("hidden");
    document.getElementById("btn-back-data").classList.add("hidden");
    document.getElementById("data-overview").classList.remove("hidden");
}

// Floating Manual Entry Modal
function toggleManualModal(show) {
    const modal = document.getElementById("manual-data-modal");
    const feedback = document.getElementById("modal-feedback");
    if (show) {
        modal.classList.remove("hidden");
        feedback.classList.add("hidden");
    } else {
        modal.classList.add("hidden");
    }
}

// Feedback styles by overall status severity
const STATUS_STYLES = {
    normal: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
    atention: "text-amber-300 bg-amber-500/10 border-amber-500/30",
    bad: "text-orange-300 bg-orange-500/10 border-orange-500/30",
    critical: "text-rose-300 bg-rose-500/10 border-rose-500/30"
};

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

// Status dot per NASA hazard, from the subject's last reading.
// Static fallback = the risk level shown on each card (NASA dataset context).
function updateHazardDots() {
    const subject = typeof getSelectedSubject === "function" ? getSelectedSubject() : "A";
    const reading = typeof getLastReading === "function" ? getLastReading(subject) : null;
    const metrics = reading ? (reading.metrics || {}) : {};

    const worst = (statuses) => {
        const order = { normal: 0, atention: 1, bad: 2, critical: 3 };
        let worstStatus = "normal";
        statuses.forEach(s => {
            if (s && order[s.split(":")[0].trim()] > order[worstStatus]) worstStatus = s.split(":")[0].trim();
        });
        return worstStatus;
    };

    const dots = {
        "py-dot-radiation": metrics.radiation ? metrics.radiation.status : "critical",
        "py-dot-isolation": metrics.mood || metrics.fatigue
            ? worst([metrics.mood && metrics.mood.status, metrics.fatigue && metrics.fatigue.status])
            : "atention",
        "py-dot-gravity": "atention",
        "py-dot-environment": metrics.cabin_co2 || metrics.spO2
            ? worst([metrics.cabin_co2 && metrics.cabin_co2.status, metrics.spO2 && metrics.spO2.status])
            : "normal",
        "py-dot-distance": metrics.reaction || metrics.sleep
            ? worst([metrics.reaction && metrics.reaction.status, metrics.sleep && metrics.sleep.status])
            : "critical"
    };

    Object.entries(dots).forEach(([id, status]) => {
        const dot = document.getElementById(id);
        if (dot) dot.style.background = statusColor(status);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    updateHazardDots();
});

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
    feedback.innerText = "📡 Sending data to the model...";

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

    // Gamification: XP, points and streak for this astronaut
    if (typeof updateProfileProgress === "function") {
        const result = updateProfileProgress(payload.subject_id, payload, response);
        if (result) {
            feedback.innerText = `${response.ai_response || "Data recorded successfully."}\n+${result.earned} pts earned!`;
        }
    }

    feedback.className = `text-xs font-semibold p-2.5 rounded-xl text-center border ${STATUS_STYLES[overall] || STATUS_STYLES.normal}`;
    feedback.innerText = response.ai_response || "Data recorded successfully.";

    setTimeout(() => {
        toggleManualModal(false);
        resetManualForm();
    }, 3500);
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
