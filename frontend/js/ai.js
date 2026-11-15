async function handleSendMessage() {
    const input = document.getElementById("py-astronaut-msg-input");
    const sendBtn = document.getElementById("py-send-btn");
    const text = input.value.trim();
    if (!text || sendBtn.disabled) return;

    appendBoxMessage("Astronauta", text);
    input.value = "";

    // Activar estado "Pensando..." en la mascota IA
    setMascotState("thinking", "Analizando datos...");
    setChatBusy(true);
    showTypingIndicator();

    let response;
    try {
        response = await PythonBridge.sendChatMessage(text);
    } catch (error) {
        response = { reply: "Hubo un problema de conexión con la IA local. Intenta de nuevo." };
    } finally {
        removeTypingIndicator();
        setChatBusy(false);
    }

    // Activar animación de "Hablando" cuando responde
    setMascotState("speaking", "Respondiendo...");
    appendBoxMessage("AstroAI Local", response.reply, response.source);

    // Volver a estado normal tras 2.5 segundos
    setTimeout(() => {
        setMascotState("idle", "Listo para analizar tus registros de salud.");
    }, 2500);
}

function setChatBusy(busy) {
    const input = document.getElementById("py-astronaut-msg-input");
    const sendBtn = document.getElementById("py-send-btn");
    input.disabled = busy;
    sendBtn.disabled = busy;
    sendBtn.classList.toggle("opacity-50", busy);
    sendBtn.classList.toggle("cursor-not-allowed", busy);
    sendBtn.innerText = busy ? "..." : "Enviar";
}

function showTypingIndicator() {
    removeTypingIndicator();
    const box = document.getElementById("py-ia-responses-box");
    const el = document.createElement("div");
    el.id = "py-typing-indicator";
    el.className = "bg-slate-900 p-3 rounded-xl border border-slate-800 flex items-center gap-1.5 w-16 justify-center";
    el.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    box.appendChild(el);
    box.scrollTop = box.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById("py-typing-indicator");
    if (el) el.remove();
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

function appendBoxMessage(sender, text, source) {
    const box = document.getElementById("py-ia-responses-box");
    const msg = document.createElement("div");
    msg.className = "bg-slate-900 p-3 rounded-xl border border-slate-800";

    const sourceChip = source
        ? `<span class="ml-2 text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 align-middle">${escapeHtml(source)}</span>`
        : "";
    msg.innerHTML = `<p class="font-bold text-blue-400 text-[11px] uppercase mb-0.5">${escapeHtml(sender)}:${sourceChip}</p><p class="text-slate-300 whitespace-pre-line">${escapeHtml(text)}</p>`;

    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}
