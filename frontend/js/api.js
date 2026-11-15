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
            // Backend offline: signal it so the UI does NOT fake a green state
            return {
                offline: true,
                overall_status: null,
                ai_response: "[Offline] The backend is not reachable. Start it with 'uvicorn main:app --port 5000' (or streamlit run frontend/app.py) and log your data again."
            };
        }
    },

    async sendChatMessage(prompt) {
        const subjectId = typeof getSelectedSubject === "function"
            ? getSelectedSubject()
            : (localStorage.getItem("selectedSubject") || "A");
        try {
            const response = await fetch(`${PYTHON_API_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt, subject_id: subjectId })
            });
            return await response.json();
        } catch (error) {
            return {
                reply: "[Local AI] The /api/chat endpoint is ready to connect with Python."
            };
        }
    }
};
