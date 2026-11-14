async function handleSendMessage() {
    const input = document.getElementById("py-astronaut-msg-input");
    const text = input.value.trim();
    if (!text) return;

    appendBoxMessage("Astronauta", text);
    input.value = "";

    // Activar estado "Pensando..." en la mascota IA
    setMascotState("thinking", "Analizando datos...");

    const response = await PythonBridge.sendChatMessage(text);
    
    // Activar animación de "Hablando" cuando responde
    setMascotState("speaking", "Respondiendo...");
    appendBoxMessage("AstroAI Local", response.reply);

    // Volver a estado normal tras 2.5 segundos
    setTimeout(() => {
        setMascotState("idle", "Listo para analizar tus registros de salud.");
    }, 2500);
}

function setMascotState(state, captionText) {
    const face = document.getElementById("ai-mascot-face");
    const badge = document.getElementById("ai-state-badge");
    const caption = document.getElementById("ai-mascot-caption");

    if (caption) caption.innerText = captionText;

    if (state === "speaking") {
        face.classList.add("speaking");
        badge.innerText = "Hablando";
        badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30";
    } else if (state === "thinking") {
        face.classList.remove("speaking");
        badge.innerText = "Procesando...";
        badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30";
    } else {
        face.classList.remove("speaking");
        badge.innerText = "En línea";
        badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
    }
}

function appendBoxMessage(sender, text) {
    const box = document.getElementById("py-ia-responses-box");
    const msg = document.createElement("div");
    msg.className = "bg-slate-900 p-3 rounded-xl border border-slate-800";
    msg.innerHTML = `<p class="font-bold text-blue-400 text-[11px] uppercase mb-0.5">${sender}:</p><p class="text-slate-300">${text}</p>`;
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}