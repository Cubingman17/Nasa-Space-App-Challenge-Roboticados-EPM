const PYTHON_API_URL = "http://localhost:5000/api";

// Shared utility: escapes text so it can be inserted safely into HTML
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
}

const PythonBridge = {
    async fetchHomeData(subjectId = "A") {
        try {
            const response = await fetch(`${PYTHON_API_URL}/home?subject=${subjectId}`);
            if (!response.ok) throw new Error("Python server offline");
            return await response.json();
        } catch (error) {
            return null;
        }
    },

    async sendSensorData(payload) {
        try {
            const response = await fetch(`${PYTHON_API_URL}/predict`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            return await response.json();
        } catch (error) {
            return {
                ai_response: `[Local Simulation] Data received for Subject ${payload.subject_id}. Predicted next reaction: ${Math.round(payload.rt_ms * 1.02)} ms.`
            };
        }
    },

    async sendChatMessage(prompt) {
        try {
            const response = await fetch(`${PYTHON_API_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt })
            });
            return await response.json();
        } catch (error) {
            return {
                reply: "[Local AI] The /api/chat endpoint is ready to connect with Python."
            };
        }
    }
};
