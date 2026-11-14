let detailChartInstance = null;

const risksDatabase = {
    radiation: {
        title: "RADIATION & BIODOSIMETRY",
        badge: "Dataset NASA LSDA",
        description: "Evaluación de aberraciones cromosómicas inducidas por radiación ionizante espacial. Justifica el monitoreo diario de biomarcadores.",
        pre: "2.4 c/cell",
        inFlight: "8.9 c/cell",
        post: "8.2 c/cell",
        chartColor: "#f43f5e",
        bgTint: "rgba(244, 63, 94, 0.12)",
        borderTint: "rgba(244, 63, 94, 0.5)",
        dataValues: [2.4, 8.9, 8.2]
    },
    gravity: {
        title: "GRAVITY (Densidad Mineral Ósea)",
        badge: "Dataset NASA OSDR",
        description: "Pérdida de masa ósea en cadera y columna vertebral por exposición prolongada a microgravedad.",
        pre: "1.18 g/cm²",
        inFlight: "1.09 g/cm²",
        post: "1.11 g/cm²",
        chartColor: "#fbbf24",
        bgTint: "rgba(251, 191, 36, 0.12)",
        borderTint: "rgba(251, 191, 36, 0.5)",
        dataValues: [1.18, 1.09, 1.11]
    },
    psicology: {
        title: "PSICOLOGY & FATIGUE (PVT)",
        badge: "Modelo Parte 1 (n=3)",
        description: "Incremento en tiempos de reacción (>500 ms = lapso) asociado a privación o desajuste del ciclo de sueño.",
        pre: "235 ms",
        inFlight: "410 ms",
        post: "260 ms",
        chartColor: "#f43f5e",
        bgTint: "rgba(244, 63, 94, 0.12)",
        borderTint: "rgba(244, 63, 94, 0.5)",
        dataValues: [235, 410, 260]
    },
    environment: {
        title: "ENVIRONMENT (Cabina / Análogo)",
        badge: "Control Ambiental",
        description: "Estabilidad de niveles de oxígeno ambiental, presión y condiciones de prueba controlada en Tierra.",
        pre: "99% Nominal",
        inFlight: "98% Nominal",
        post: "99% Nominal",
        chartColor: "#10b981",
        bgTint: "rgba(16, 185, 129, 0.12)",
        borderTint: "rgba(16, 185, 129, 0.5)",
        dataValues: [99, 98, 99]
    }
};

// Abre cualquiera de las 4 pestañas de datos y dibuja su gráfica
function openRiskDetail(riskKey) {
    const info = risksDatabase[riskKey];
    if (!info) return;

    const overview = document.getElementById("data-overview");
    const detailView = document.getElementById("data-detail-view");
    const backBtn = document.getElementById("btn-back-data");

    if (overview) overview.style.display = "none";
    if (detailView) detailView.style.display = "grid";
    if (backBtn) backBtn.style.display = "inline-flex";

    document.getElementById("detail-badge").innerText = info.badge;
    document.getElementById("detail-title").innerText = info.title;
    document.getElementById("detail-description").innerText = info.description;
    document.getElementById("stat-pre").innerText = info.pre;
    document.getElementById("stat-in").innerText = info.inFlight;
    document.getElementById("stat-post").innerText = info.post;

    const chartContainer = document.getElementById("detail-chart-container");
    chartContainer.style.backgroundColor = info.bgTint;
    chartContainer.style.borderColor = info.borderTint;

    const canvas = document.getElementById("riskDetailChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    if (detailChartInstance) {
        detailChartInstance.destroy();
    }

    detailChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Pre-Vuelo", "En Vuelo", "Post-Vuelo"],
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

// Regresa a la vista de los 4 indicadores
function closeRiskDetail() {
    const overview = document.getElementById("data-overview");
    const detailView = document.getElementById("data-detail-view");
    const backBtn = document.getElementById("btn-back-data");

    if (detailView) detailView.style.display = "none";
    if (backBtn) backBtn.style.display = "none";
    if (overview) overview.style.display = "flex";
}

// Abre o cierra el modal de ingreso manual
function toggleManualModal(show) {
    const modal = document.getElementById("manual-data-modal");
    const feedback = document.getElementById("modal-feedback");
    if (!modal) return;

    if (show) {
        modal.style.display = "flex";
        if (feedback) feedback.style.display = "none";
    } else {
        modal.style.display = "none";
    }
}

// Envía los datos manuales y actualiza colores en toda la app
async function submitManualSensors() {
    const payload = {
        hr_bpm: document.getElementById("py-input-lpm").value,
        spo2_pct: document.getElementById("py-input-spo2").value,
        sleep_hours: document.getElementById("py-input-sleep").value,
        rt_ms: document.getElementById("py-input-rt").value,
        fatigue_level: document.getElementById("py-input-fatigue").value,
        env_temp: document.getElementById("py-input-temp").value,
        notes: document.getElementById("py-input-notes").value
    };

    const feedback = document.getElementById("modal-feedback");
    feedback.style.display = "block";

    if (!payload.hr_bpm || !payload.sleep_hours || !payload.rt_ms) {
        feedback.className = "text-xs font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-xl text-center";
        feedback.innerText = "⚠️ Completa al menos LPM, Sueño y Tiempo de Reacción.";
        return;
    }

    if (typeof PythonBridge !== "undefined") {
        const response = await PythonBridge.sendSensorData(payload);
        feedback.className = "text-xs font-semibold text-emerald-300 bg-emerald-500/10 border border-emerald-500/30 p-2.5 rounded-xl text-center";
        feedback.innerText = `✅ ${response.ai_response || "Estado actualizado correctamente."}`;
    } else {
        feedback.className = "text-xs font-semibold text-rose-300 bg-rose-500/10 border border-rose-500/30 p-2.5 rounded-xl text-center";
        feedback.innerText = "⚠️ Error: Verifica que js/api.js esté cargado.";
    }
}