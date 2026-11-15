document.addEventListener("DOMContentLoaded", async () => {
    // 1. Animación de escritura (Typewriter) para el texto WELCOME
    const subject = typeof getSelectedSubject === "function"
        ? getSelectedSubject()
        : (localStorage.getItem("selectedSubject") || "A");
    const profile = typeof getProfile === "function" ? getProfile(subject) : null;
    const welcomeText = `WELCOME, ASTRONAUT ${(profile ? profile.name : subject).toUpperCase()}`;
    const welcomeElement = document.getElementById("welcome-typewriter");

    let index = 0;
    function typeWriterEffect() {
        if (index < welcomeText.length) {
            welcomeElement.textContent += welcomeText.charAt(index);
            index++;
            setTimeout(typeWriterEffect, 65);
        }
    }
    typeWriterEffect();

    // 2. Health Radar: the 5 core metrics of the last reading, scored by status
    const reading = typeof getLastReading === "function" ? getLastReading(subject) : null;
    const radarLabels = ["BPM", "SpO2", "Sleep", "Reaction", "Fatigue"];
    const metricKeys = ["bpm", "spO2", "sleep", "reaction", "fatigue"];

    let scores;
    let radarColor = "#3b82f6";
    if (reading && reading.metrics) {
        scores = metricKeys.map(key => statusScore(reading.metrics[key] && reading.metrics[key].status));
        radarColor = statusColor(reading.overall_status);
    } else {
        scores = [0, 0, 0, 0, 0];
    }

    const caption = document.getElementById("py-radar-caption");
    if (caption) {
        caption.innerText = reading
            ? `Last reading: ${radarLabels.map((label, i) =>
                `${label} ${reading.metrics[metricKeys[i]].value}${reading.metrics[metricKeys[i]].unit}`).join(" | ")}`
            : "No data logged yet — enter your metrics in the DATA tab.";
    }

    const ctx = document.getElementById("homePieChart").getContext("2d");
    new Chart(ctx, {
        type: "radar",
        data: {
            labels: radarLabels,
            datasets: [{
                label: "Health score",
                data: scores,
                backgroundColor: radarColor + "33",
                borderColor: radarColor,
                pointBackgroundColor: scores.map((score, i) =>
                    score > 0 ? statusColor(reading.metrics[metricKeys[i]].status) : "#475569"),
                pointBorderColor: "#0a1120",
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: { display: false, stepSize: 25 },
                    grid: { color: "rgba(255,255,255,0.10)" },
                    angleLines: { color: "rgba(255,255,255,0.10)" },
                    pointLabels: { color: "#cbd5e1", font: { size: 11, weight: "bold" } }
                }
            }
        }
    });

    // 3. Leaderboard dinámico desde los perfiles
    if (typeof computeRanking === "function") {
        const container = document.getElementById("py-leaderboard-list");
        if (container) {
            const medals = ["🥇", "🥈", "🥉"];
            container.innerHTML = "";
            computeRanking().forEach((p, i) => {
                const item = document.createElement("div");
                item.className = "leaderboard-item flex items-center justify-between px-3 py-2 text-xs md:text-sm font-semibold";
                const highlight = p.id === subject ? "text-blue-300" : "text-white";
                item.innerHTML = `<span>${medals[i] || (i + 1) + "."} <strong class="${highlight}">${escapeHtml(p.name)}</strong></span>
                    <span class="flex items-center gap-2">
                        <span class="text-amber-400" title="${p.streak || 0} day logging streak">&#128293; ${p.streak || 0}d</span>
                        <span class="text-blue-400 font-extrabold">${p.points} pts</span>
                    </span>`;
                container.appendChild(item);
            });
        }
    }

    // 4. Conectar con datos reales desde Python si está activo
    const pythonData = await PythonBridge.fetchHomeData(subject);
    if (pythonData) {
        if (pythonData.missions) {
            document.getElementById("py-home-missions").innerText = pythonData.missions;
        }
    }
});
