// Applies the astronaut's health state to the interface:
// console border (green/yellow/red) and the HOME status badge.
function applyHealthState(status) {
    const frameClass = {
        normal: "state-green",
        atention: "state-yellow",
        bad: "state-yellow",
        critical: "state-red"
    }[status];
    if (!frameClass) return;

    const frame = document.querySelector(".tablet-frame");
    if (frame) {
        frame.classList.remove("state-green", "state-yellow", "state-red");
        frame.classList.add(frameClass);
    }

    const badge = document.getElementById("py-home-status");
    if (badge) {
        const conf = {
            normal: ["STATUS: OPTIMAL", "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"],
            atention: ["STATUS: ATTENTION", "bg-amber-500/20 text-amber-300 border-amber-500/30"],
            bad: ["STATUS: POOR", "bg-orange-500/20 text-orange-300 border-orange-500/30"],
            critical: ["STATUS: CRITICAL", "bg-rose-500/20 text-rose-300 border-rose-500/30"]
        }[status];
        if (conf) {
            badge.innerText = conf[0];
            badge.className = "text-xs font-bold px-3 py-1 rounded-full border " + conf[1];
        }
    }
}

// Pretty banner: overall pill + one chip per metric with a status dot
// + actionable suggestions for the metrics that are not optimal
function renderAdviceBanner(el, reading) {
    const overall = String(reading.overall_status || "normal").split(":")[0].trim().toUpperCase();
    const pillClass = {
        NORMAL: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
        ATENTION: "bg-amber-500/20 text-amber-300 border-amber-500/40",
        BAD: "bg-orange-500/20 text-orange-300 border-orange-500/40",
        CRITICAL: "bg-rose-500/20 text-rose-300 border-rose-500/40"
    }[overall] || "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";

    let chips = "";
    for (const metric of Object.values(reading.metrics || {})) {
        const color = statusColor(metric.status);
        chips += `<span class="inline-flex items-center gap-1.5 bg-slate-900/80 border border-slate-700 rounded-full px-2.5 py-0.5">
            <span class="w-2 h-2 rounded-full" style="background:${color}"></span>
            <span class="font-bold text-slate-200">${escapeHtml(metric.label)}</span>
            <span class="text-slate-400">${escapeHtml(String(metric.value))}${escapeHtml(metric.unit)}</span>
        </span>`;
    }

    let suggestionsHtml = "";
    const suggestions = reading.suggestions || [];
    if (suggestions.length) {
        const items = suggestions.map(tip =>
            `<li class="flex items-start gap-1.5"><span class="text-amber-400 mt-0.5">▸</span><span>${escapeHtml(tip)}</span></li>`
        ).join("");
        suggestionsHtml = `
            <div class="mt-1.5 pt-1.5 border-t border-slate-700/60">
                <p class="text-[10px] font-extrabold uppercase tracking-wider text-amber-300 mb-0.5">How to improve your metrics:</p>
                <ul class="space-y-0.5">${items}</ul>
            </div>`;
    }

    el.innerHTML = `
        <div class="flex flex-col gap-1.5 w-full">
            <div class="flex items-center gap-2 flex-wrap">
                <strong class="text-blue-400">Little AI Advice:</strong>
                <span class="text-[10px] font-extrabold px-2 py-0.5 rounded-full border ${pillClass}">OVERALL: ${overall}</span>
            </div>
            <div class="flex flex-wrap gap-1.5">${chips}</div>
            ${suggestionsHtml}
        </div>`;
}

document.addEventListener("DOMContentLoaded", () => {
    const savedSubject = typeof getSelectedSubject === "function"
        ? getSelectedSubject()
        : (localStorage.getItem("selectedSubject") || "A");
    const userLabel = document.getElementById("py-home-user");
    if (userLabel) {
        const profile = typeof getProfile === "function" ? getProfile(savedSubject) : null;
        userLabel.innerText = `ASTRONAUT ${profile ? profile.name.toUpperCase() : savedSubject}`;
    }

    // Restore the subject's last known health state
    const status = localStorage.getItem(`lastOverallStatus_${savedSubject}`);
    if (status) applyHealthState(status);

    // Show the subject's last AI advice in the banners of each page
    const reading = typeof getLastReading === "function" ? getLastReading(savedSubject) : null;
    const lastAdvice = localStorage.getItem(`lastAiResponse_${savedSubject}`);
    ["py-home-ai-advice", "py-data-ai-advice", "py-profile-ai-advice"].forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (reading) {
            renderAdviceBanner(el, reading);
        } else if (lastAdvice) {
            el.innerHTML = `<strong class="text-blue-400">Little AI Advice:</strong> ${escapeHtml(lastAdvice)}`;
        }
    });

    // Main page: warn clearly when the local AI (Ollama) is not running
    if (typeof PythonBridge !== "undefined" && typeof PythonBridge.fetchAiStatus === "function") {
        PythonBridge.fetchAiStatus().then((status) => {
            if (status.ollama) return;
            const target = document.getElementById("py-home-ai-advice");
            if (!target) return;
            const warning = document.createElement("div");
            warning.id = "ai-offline-warning";
            warning.className = "mb-2 p-2.5 rounded-xl border border-rose-500/40 bg-rose-500/10 text-rose-200 text-xs font-semibold leading-snug";
            warning.innerHTML = "&#9888;&#65039; The local AI (Ollama) is not running — this console does not work well without it. "
                + "AI advice and the AstroAI chat are limited. Start Ollama (<b>ollama serve</b>) for the full experience.";
            target.prepend(warning);
        });
    }
});
