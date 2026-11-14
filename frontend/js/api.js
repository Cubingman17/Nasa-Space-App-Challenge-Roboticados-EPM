const PYTHON_API_URL = "http://localhost:5000/api";

const PythonBridge = {
    async fetchHomeData(subjectId = "A") {
        try {
            const response = await fetch(`${PYTHON_API_URL}/home?subject=${subjectId}`);
            if (!response.ok) throw new Error("Servidor Python offline");
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
                ai_response: `[Simulación Local] Datos recibidos para Sujeto ${payload.subject_id}. Predicción siguiente reacción: ${Math.round(payload.rt_ms * 1.02)} ms.`
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
                reply: "[IA Local en entrenamiento] Endpoint /api/chat listo para conectar con Python."
            };
        }
    }
};