async function handleSendMessage() {
    const input = document.getElementById("py-astronaut-msg-input");
    const sendBtn = document.getElementById("py-send-btn");
    const text = input.value.trim();
    if (!text || sendBtn.disabled) return;

    appendBoxMessage("Astronaut", text);
    input.value = "";

    // Activate the mascot's "Thinking..." state
    setMascotState("thinking", "Analyzing data...");
    setChatBusy(true);
    showTypingIndicator();

    let response;
    try {
        response = await PythonBridge.sendChatMessage(text);
    } catch (error) {
        response = { reply: "There was a connection problem with the local AI. Try again." };
    } finally {
        removeTypingIndicator();
        setChatBusy(false);
    }

    // Activate the "Speaking" animation when it replies
    setMascotState("speaking", "Replying...");
    appendBoxMessage("AstroAI Local", response.reply, response.source);

    // Fallback mode: make it explicit when the local LLM is not running
    if (response.source && response.source !== "local-llm") {
        appendBoxMessage("System",
            "AstroAI (Ollama) is offline. Fallback mode: rule-based analysis of your logged metrics. " +
            "Start it with 'ollama serve' and 'ollama run astroai' to talk with the local AI.",
            "fallback");
    }

    // Back to normal after 2.5 seconds
    setTimeout(() => {
        setMascotState("idle", "Ready to analyze your health records.");
    }, 2500);
}

function setChatBusy(busy) {
    const input = document.getElementById("py-astronaut-msg-input");
    const sendBtn = document.getElementById("py-send-btn");
    input.disabled = busy;
    sendBtn.disabled = busy;
    sendBtn.classList.toggle("opacity-50", busy);
    sendBtn.classList.toggle("cursor-not-allowed", busy);
    sendBtn.innerText = busy ? "..." : "Send";
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
        badge.innerText = "Speaking";
        badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30";
    } else if (state === "thinking") {
        face.classList.remove("speaking");
        badge.innerText = "Processing...";
        badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30";
    } else {
        face.classList.remove("speaking");
        badge.innerText = "Online";
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
