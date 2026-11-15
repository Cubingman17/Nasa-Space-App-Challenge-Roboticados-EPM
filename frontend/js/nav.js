// Aplica el estado de salud del astronauta a la interfaz:
// borde de la consola (verde/amarillo/rojo) y badge de estado del HOME.
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
            normal: ["ESTADO: ÓPTIMO", "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"],
            atention: ["ESTADO: ATENCIÓN", "bg-amber-500/20 text-amber-300 border-amber-500/30"],
            bad: ["ESTADO: GRAVE", "bg-orange-500/20 text-orange-300 border-orange-500/30"],
            critical: ["ESTADO: CRÍTICO", "bg-rose-500/20 text-rose-300 border-rose-500/30"]
        }[status];
        if (conf) {
            badge.innerText = conf[0];
            badge.className = "text-xs font-bold px-3 py-1 rounded-full border " + conf[1];
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const savedSubject = localStorage.getItem("selectedSubject") || "A";
    const userLabel = document.getElementById("py-home-user");
    if (userLabel) {
        userLabel.innerText = `ASTRONAUTA ${savedSubject}`;
    }

    // Restaurar el último estado de salud conocido
    const status = localStorage.getItem("lastOverallStatus");
    if (status) applyHealthState(status);

    // Mostrar el último consejo de la IA en los banners de cada página
    const lastAdvice = localStorage.getItem("lastAiResponse");
    if (lastAdvice) {
        ["py-home-ai-advice", "py-data-ai-advice", "py-profile-ai-advice"].forEach((id) => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = `<strong class="text-blue-400">Little AI Advice:</strong> ${escapeHtml(lastAdvice)}`;
            }
        });
    }
});
