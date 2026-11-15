const DATA_API_URL = `${PYTHON_API_URL}/data`;
const datasetCharts = [];
const categoryCountIds = {
    radiation: "category-count-radiation",
    microgravity: "category-count-microgravity",
    psychology: "category-count-psychology",
    environment: "category-count-environment"
};
const chartColors = ["#38bdf8", "#a78bfa", "#fb7185", "#34d399", "#fbbf24"];

async function requestDataApi(path) {
    const response = await fetch(`${DATA_API_URL}${path}`);
    if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `Data API request failed (${response.status})`);
    }
    return response.json();
}

async function loadDataCategories() {
    try {
        const payload = await requestDataApi("");
        for (const category of payload.categories || []) {
            const count = document.getElementById(categoryCountIds[category.id]);
            if (count) {
                count.textContent = `${category.metrics.length} metric tables · ${category.observation_count} records`;
            }
        }
    } catch (error) {
        Object.values(categoryCountIds).forEach((id) => {
            const count = document.getElementById(id);
            if (count) count.textContent = "Data service unavailable";
        });
    }
}

function clearDatasetCharts() {
    while (datasetCharts.length) datasetCharts.pop().destroy();
}

function humanizeFieldName(value) {
    return value.replaceAll("_", " ").replace(/\b[a-z]/g, (letter) => letter.toUpperCase());
}

function createRawTable(records, container) {
    if (!records.length) return;

    const detail = document.createElement("details");
    detail.className = "mt-4 rounded-xl border border-slate-700 bg-slate-950/60";
    const summary = document.createElement("summary");
    summary.className = "cursor-pointer px-3 py-2 text-xs font-bold text-slate-300";
    summary.textContent = `View source table (${records.length} records)`;
    detail.appendChild(summary);

    const tableWrap = document.createElement("div");
    tableWrap.className = "overflow-x-auto max-h-72";
    const table = document.createElement("table");
    table.className = "min-w-full text-left text-[11px] text-slate-300";
    const fieldNames = [...new Set(records.flatMap((record) => Object.keys(record.values || {})))];
    const columns = ["measurement_id", "astronaut_id", "timestamp", ...fieldNames];
    const thead = document.createElement("thead");
    thead.className = "sticky top-0 bg-slate-800 text-slate-200";
    const headerRow = document.createElement("tr");
    columns.forEach((column) => {
        const th = document.createElement("th");
        th.className = "px-3 py-2 whitespace-nowrap";
        th.textContent = humanizeFieldName(column);
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    records.forEach((record) => {
        const row = document.createElement("tr");
        row.className = "border-t border-slate-800";
        const values = [record.measurement_id, record.astronaut_id, record.timestamp];
        fieldNames.forEach((field) => values.push(record.values?.[field]));
        values.forEach((value) => {
            const cell = document.createElement("td");
            cell.className = "px-3 py-1.5 whitespace-nowrap";
            cell.textContent = value == null ? "—" : String(value);
            row.appendChild(cell);
        });
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    tableWrap.appendChild(table);
    detail.appendChild(tableWrap);
    container.appendChild(detail);
}

function renderMetricCharts(metric, payload, chartGrid) {
    const series = payload.series || [];
    if (!series.length) {
        const message = document.createElement("p");
        message.className = "text-xs text-slate-400";
        message.textContent = "No numeric columns are available to graph.";
        chartGrid.appendChild(message);
        return;
    }

    series.forEach((line, index) => {
        const chartCard = document.createElement("div");
        chartCard.className = "rounded-xl border border-slate-700 bg-slate-950/60 p-3";
        const title = document.createElement("h5");
        title.className = "mb-2 text-xs font-bold text-slate-200";
        title.textContent = humanizeFieldName(line.key);
        const canvasWrap = document.createElement("div");
        canvasWrap.className = "relative h-56";
        const canvas = document.createElement("canvas");
        canvas.setAttribute("aria-label", `${metric.name}: ${humanizeFieldName(line.key)}`);
        canvasWrap.appendChild(canvas);
        chartCard.append(title, canvasWrap);
        chartGrid.appendChild(chartCard);

        const points = line.points || [];
        const color = chartColors[index % chartColors.length];
        datasetCharts.push(new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels: points.map((point) => new Date(point.timestamp).toLocaleString()),
                datasets: [{
                    label: humanizeFieldName(line.key),
                    data: points.map((point) => point.value),
                    borderColor: color,
                    backgroundColor: `${color}22`,
                    pointRadius: 2,
                    borderWidth: 2,
                    tension: 0.2,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: "index" },
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        grid: { color: "rgba(255,255,255,0.06)" },
                        ticks: { color: "#94a3b8", maxTicksLimit: 7, maxRotation: 0 }
                    },
                    y: {
                        grid: { color: "rgba(255,255,255,0.08)" },
                        ticks: { color: "#cbd5e1" }
                    }
                }
            }
        }));
    });
}

async function renderMetricDataset(metric, container) {
    const card = document.createElement("article");
    card.className = "ui-card p-4 md:p-5";
    const header = document.createElement("div");
    header.className = "mb-3 flex flex-wrap items-start justify-between gap-2 border-b border-slate-700 pb-3";
    const headingGroup = document.createElement("div");
    const title = document.createElement("h4");
    title.className = "font-extrabold text-sm md:text-base text-white";
    title.textContent = `${String(metric.id).padStart(2, "0")} · ${metric.name}`;
    const description = document.createElement("p");
    description.className = "mt-1 text-xs text-slate-400";
    description.textContent = metric.description;
    headingGroup.append(title, description);
    const recordCount = document.createElement("span");
    recordCount.className = "rounded-lg bg-slate-800 px-2 py-1 text-[10px] font-bold text-slate-300";
    recordCount.textContent = `${metric.observation_count || 0} records`;
    header.append(headingGroup, recordCount);
    const chartGrid = document.createElement("div");
    chartGrid.className = "grid grid-cols-1 xl:grid-cols-2 gap-3";
    card.append(header, chartGrid);
    container.appendChild(card);

    try {
        const payload = await requestDataApi(`/metrics/${metric.id}/observations`);
        recordCount.textContent = `${payload.observations.length} records`;
        if (payload.observations.length) {
            renderMetricCharts(metric, payload, chartGrid);
            createRawTable(payload.observations, card);
        } else {
            const empty = document.createElement("p");
            empty.className = "text-xs text-slate-400";
            empty.textContent = "No records imported for this dataset yet.";
            chartGrid.appendChild(empty);
        }
    } catch (error) {
        const message = document.createElement("p");
        message.className = "text-xs text-rose-300";
        message.textContent = `Could not load this dataset: ${error.message}`;
        chartGrid.appendChild(message);
    }
}

async function openRiskDetail(categoryId) {
    clearDatasetCharts();
    document.getElementById("data-overview").classList.add("hidden");
    document.getElementById("data-detail-view").classList.remove("hidden");
    document.getElementById("btn-back-data").classList.remove("hidden");

    const title = document.getElementById("detail-title");
    const description = document.getElementById("detail-description");
    const status = document.getElementById("dataset-load-status");
    const container = document.getElementById("metric-datasets");
    const categoryName = categoryId.charAt(0).toUpperCase() + categoryId.slice(1);
    title.textContent = categoryName;
    description.textContent = "Loading metric tables and charts…";
    status.textContent = "";
    container.replaceChildren();

    try {
        const category = await requestDataApi(`/${encodeURIComponent(categoryId)}`);
        title.textContent = category.name;
        description.textContent = category.description;
        status.textContent = `${category.metrics.length} metric tables · ${category.observation_count} total records`;
        await Promise.all(category.metrics.map((metric) => renderMetricDataset(metric, container)));
    } catch (error) {
        description.textContent = "Could not load this category.";
        status.textContent = error.message;
    }
}

function closeRiskDetail() {
    clearDatasetCharts();
    document.getElementById("data-detail-view").classList.add("hidden");
    document.getElementById("btn-back-data").classList.add("hidden");
    document.getElementById("data-overview").classList.remove("hidden");
}

loadDataCategories();
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
