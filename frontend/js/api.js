const PYTHON_API_URL = "http://localhost:5000/api";

// Estructura estándar que Python debe enviar al Frontend
const DEFAULT_PYTHON_STATE = {
    overall_status: "green", // "green" | "yellow" | "red"
    status_label: "ÓPTIMO (Z < 1.5)",
    level: 4,
    xp_percent: 78,
    ai_advice: "Tus horas de sueño (7.5h) y estabilidad cardíaca aseguran un óptimo desempeño hoy.",
    risks: {
        radiation: { level: "ALTO", color: "red" },
        gravity: { level: "MODERADO", color: "yellow" },
        psicology: { level: "BAJO", color: "green" },
        environment: { level: "ÓPTIMO", color: "green" }
    }
};

const PythonBridge = {
    // Obtener estado actual desde el servidor Python
    async syncStateFromPython() {
        try {
            const response = await fetch(`${PYTHON_API_URL}/status`);
            if (!response.ok) throw new Error("Python backend offline");
            const data = await response.json();
            localStorage.setItem("astroState", JSON.stringify(data));
            applyPythonStateToUI(data);
            return data;
        } catch (error) {
            const cached = JSON.parse(localStorage.getItem("astroState")) || DEFAULT_PYTHON_STATE;
            applyPythonStateToUI(cached);
            return cached;
        }
    },

    // Enviar datos de sensores manuales a Python y recibir nuevo color/estado
    async sendSensorData(payload) {
        try {
            const response = await fetch(`${PYTHON_API_URL}/predict`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const updatedState = await response.json();
            localStorage.setItem("astroState", JSON.stringify(updatedState));
            applyPythonStateToUI(updatedState);
            return updatedState;
        } catch (error) {
            // Cálculo local temporal mientras conectas Python (Regla Z-Score / Lapsos)
            const rt = parseFloat(payload.rt_ms) || 240;
            const sleep = parseFloat(payload.sleep_hours) || 7.5;
            const hr = parseFloat(payload.hr_bpm) || 68;

            let status = "green";
            let label = "ÓPTIMO (Z < 1.5)";
            let advice = "Parámetros estables dentro de tu línea base personal.";
            let psicoColor = "green";
            let psicoLevel = "BAJO";

            if (rt > 500 || sleep < 5.5 || hr > 100) {
                status = "red";
                label = "ALERTA CRÍTICA (Z > 2.5)";
                advice = `Alerta: Tiempo de reacción (${rt}ms) o sueño (${sleep}h) fuera de rango. Se recomienda descanso inmediato.`;
                psicoColor = "red";
                psicoLevel = "ALTO";
            } else if (rt > 350 || sleep < 6.5 || hr > 85) {
                status = "yellow";
                label = "PRECAUCIÓN (Z 1.5 - 2.5)";
                advice = `Desviación moderada detectada. Prioriza recuperar horas de sueño hoy.`;
                psicoColor = "yellow";
                psicoLevel = "MODERADO";
            }

            const simulatedState = {
                overall_status: status,
                status_label: label,
                level: status === "green" ? 5 : 4,
                xp_percent: status === "green" ? 90 : 65,
                ai_advice: advice,
                risks: {
                    radiation: { level: "ALTO", color: "red" },
                    gravity: { level: "MODERADO", color: "yellow" },
                    psicology: { level: psicoLevel, color: psicoColor },
                    environment: { level: "ÓPTIMO", color: "green" }
                }
            };

            localStorage.setItem("astroState", JSON.stringify(simulatedState));
            applyPythonStateToUI(simulatedState);
            return {
                ...simulatedState,
                ai_response: `[Estado actualizado a ${status.toUpperCase()}] ${advice}`
            };
        }
    },

    // Chat con Google AI Studio o Simulación
    async sendChatMessage(prompt) {
        const tempApiKey = (localStorage.getItem("tempAiApiKey") || "").trim();

        if (tempApiKey.length > 10) {
            const models = ["gemini-2.5-flash", "gemini-2.0-flash"];
            for (const model of models) {
                try {
                    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(tempApiKey)}`;
                    const res = await fetch(url, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            contents: [{
                                role: "user",
                                parts: [{ text: `Eres AstroBot, IA de salud espacial (prototipo educativo, no médico). Responde breve a: ${prompt}` }]
                            }]
                        })
                    });
                    const data = await res.json();
                    if (res.ok && data.candidates?.[0]?.content?.parts?.[0]?.text) {
                        return { reply: data.candidates[0].content.parts[0].text, source: `Gemini (${model})` };
                    }
                } catch (e) {}
            }
        }

        const currentState = JSON.parse(localStorage.getItem("astroState")) || DEFAULT_PYTHON_STATE;
        return {
            reply: `[Modo Simulado - Estado ${currentState.overall_status.toUpperCase()}] ${currentState.ai_advice}`,
            source: "AstroBot Local"
        };
    }
};

// =========================================================================
// FUNCIÓN GLOBAL QUE PINTA LOS COLORES EN TODAS LAS VISTAS SEGÚN PYTHON
// =========================================================================
function applyPythonStateToUI(state) {
    if (!state) return;

    // 1. Cambiar el marco de la tablet según el estado (Verde, Amarillo o Rojo)
    const frame = document.querySelector(".tablet-frame");
    if (frame) {
        frame.classList.remove("state-green", "state-yellow", "state-red");
        frame.classList.add(`state-${state.overall_status}`);
    }

    // 2. Actualizar píldora de estado y barra de XP en HOME
    const statusPill = document.getElementById("py-home-status");
    if (statusPill) {
        statusPill.innerText = `ESTADO: ${state.status_label}`;
        const pillColors = {
            green: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
            yellow: "bg-amber-500/20 text-amber-300 border-amber-500/40",
            red: "bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse"
        };
        statusPill.className = `text-xs font-extrabold px-3 py-1 rounded-full border ${pillColors[state.overall_status]}`;
    }

    const levelBadge = document.getElementById("py-home-level");
    const xpFill = document.getElementById("py-home-xp-bar");
    if (levelBadge) levelBadge.innerText = `LVL ${state.level || 4}`;
    if (xpFill) xpFill.style.width = `${state.xp_percent || 75}%`;

    // 3. Actualizar Little AI Advice en cualquier pantalla donde esté presente
    ["py-home-ai-advice", "py-data-ai-advice", "py-profile-ai-advice"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = `<strong class="text-blue-400">Little AI Advice:</strong> ${state.ai_advice}`;
        }
    });

    // 4. Actualizar tarjetas de riesgo en DATA si existen
    if (state.risks) {
        const colorMap = {
            red: "bg-[#ef4444] text-slate-950",
            yellow: "bg-[#fde047] text-slate-950",
            green: "bg-[#65a30d] text-slate-950"
        };
        Object.keys(state.risks).forEach(key => {
            const badge = document.getElementById(`badge-${key}`);
            if (badge) {
                const riskInfo = state.risks[key];
                badge.className = `w-1/3 flex flex-col items-center justify-center font-extrabold text-xs md:text-sm tracking-wide rounded-r-xl shadow-inner transition-colors duration-300 ${colorMap[riskInfo.color] || colorMap.green}`;
                badge.innerHTML = `<span>${key.toUpperCase()}</span><span class="text-xs font-bold mt-0.5">Risk: ${riskInfo.level}</span>`;
            }
        });
    }

    // 5. Actualizar color del visor de la mascota en IA
    const mascotRing = document.getElementById("ai-mascot-face");
    if (mascotRing) {
        const ringColors = {
            green: "border-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.3)]",
            yellow: "border-amber-400 shadow-[0_0_30px_rgba(245,158,11,0.3)]",
            red: "border-rose-500 shadow-[0_0_35px_rgba(244,63,94,0.45)]"
        };
        mascotRing.className = `ai-avatar-ring w-36 h-36 md:w-44 md:h-44 rounded-full bg-slate-950 border-4 flex flex-col items-center justify-center relative my-auto ${ringColors[state.overall_status]}`;
    }
}

// Sincronizar colores automáticamente al abrir cualquier página
document.addEventListener("DOMContentLoaded", () => {
    PythonBridge.syncStateFromPython();
});