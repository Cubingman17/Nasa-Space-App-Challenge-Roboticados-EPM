async function handleSendSensors() {
    const payload = {
        subject_id: localStorage.getItem("selectedSubject") || "A",
        hr_bpm: document.getElementById("py-input-lpm").value,
        spo2_pct: document.getElementById("py-input-spo2").value,
        sleep_hours: document.getElementById("py-input-sleep").value,
        rt_ms: document.getElementById("py-input-rt").value
    };

    if (!payload.hr_bpm || !payload.sleep_hours || !payload.rt_ms) {
        appendBoxMessage("Sistema", "⚠️ Por favor completa LPM, Sueño y Tiempo de Reacción.");
        return;
    }

    appendBoxMessage("Sensores", `LPM: ${payload.hr_bpm} | SpO2: ${payload.spo2_pct || "N/A"}% | Sueño: ${payload.sleep_hours}h | RT: ${payload.rt_ms}ms`);
    
    const response = await PythonBridge.sendSensorData(payload);
    appendBoxMessage("AstroAI (Python)", response.ai_response);
}

async function handleSendMessage() {
    const input = document.getElementById("py-astronaut-msg-input");
    const text = input.value.trim();
    if (!text) return;

    appendBoxMessage("Astronauta", text);
    input.value = "";

    const response = await PythonBridge.sendChatMessage(text);
    appendBoxMessage("AstroAI Local", response.reply);
}

function appendBoxMessage(sender, text) {
    const box = document.getElementById("py-ia-responses-box");
    const msg = document.createElement("div");
    msg.className = "bg-slate-900 p-3 rounded-xl border border-slate-800";
    msg.innerHTML = `<p class="font-bold text-blue-400 text-[11px] uppercase mb-0.5">${sender}:</p><p class="text-slate-300">${text}</p>`;
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
}