let detailChartInstance = null;

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
    psicology: {
        title: "PSYCHOLOGY & FATIGUE (PVT)",
        badge: "Part 1 Model (n=3)",
        description: "Increase in reaction times (>500 ms = lapse) associated with sleep deprivation or cycle disruption.",
        pre: "235 ms",
        inFlight: "410 ms",
        post: "260 ms",
        chartColor: "#f43f5e",
        bgTint: "rgba(244, 63, 94, 0.12)",
        borderTint: "rgba(244, 63, 94, 0.5)",
        dataValues: [235, 410, 260]
    },
    environment: {
        title: "ENVIRONMENT (Cabin / Analog)",
        badge: "Environmental Control",
        description: "Stability of ambient oxygen levels, pressure and controlled test conditions on Earth.",
        pre: "99% Nominal",
        inFlight: "98% Nominal",
        post: "99% Nominal",
        chartColor: "#10b981",
        bgTint: "rgba(16, 185, 129, 0.12)",
        borderTint: "rgba(16, 185, 129, 0.5)",
        dataValues: [99, 98, 99]
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

async function submitManualSensors() {
    const payload = {
        subject_id: localStorage.getItem("selectedSubject") || "A",
        hr_bpm: document.getElementById("py-input-lpm").value,
        spo2_pct: document.getElementById("py-input-spo2").value,
        sleep_hours: document.getElementById("py-input-sleep").value,
        rt_ms: document.getElementById("py-input-rt").value,
        fatigue_level: document.getElementById("py-input-fatigue").value,
        env_temp: document.getElementById("py-input-temp").value,
        notes: document.getElementById("py-input-notes").value
    };

    const feedback = document.getElementById("modal-feedback");
    const submitBtn = document.getElementById("py-submit-sensors");
    feedback.classList.remove("hidden");

    if (!payload.hr_bpm || !payload.sleep_hours || !payload.rt_ms) {
        feedback.className = "text-xs font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-xl text-center";
        feedback.innerText = "⚠️ Complete at least HR, Sleep and Reaction Time.";
        return;
    }

    submitBtn.disabled = true;
    feedback.className = "text-xs font-semibold text-sky-300 bg-sky-500/10 border border-sky-500/30 p-2.5 rounded-xl text-center";
    feedback.innerText = "📡 Sending data to the model...";

    const response = await PythonBridge.sendSensorData(payload);

    submitBtn.disabled = false;

    // Save the state for the console border and the AI banners
    const overall = String(response.overall_status || "normal").split(":")[0].trim();
    try {
        localStorage.setItem("lastOverallStatus", overall);
        localStorage.setItem("lastAiResponse", response.ai_response || "");
    } catch (error) {
        // localStorage unavailable: continue without persisting
    }
    if (typeof applyHealthState === "function") applyHealthState(overall);

    feedback.className = `text-xs font-semibold p-2.5 rounded-xl text-center border ${STATUS_STYLES[overall] || STATUS_STYLES.normal}`;
    feedback.innerText = response.ai_response || "Data recorded successfully.";

    setTimeout(() => {
        toggleManualModal(false);
        resetManualForm();
    }, 3500);
}

function resetManualForm() {
    ["py-input-lpm", "py-input-spo2", "py-input-sleep", "py-input-rt",
     "py-input-fatigue", "py-input-temp", "py-input-notes"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
}
