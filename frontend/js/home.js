document.addEventListener("DOMContentLoaded", async () => {
    // 1. Animación de escritura (Typewriter) para el texto WELCOME
    const subject = localStorage.getItem("selectedSubject") || "A";
    const welcomeText = `WELCOME, ASTRONAUT ${subject}`;
    const welcomeElement = document.getElementById("welcome-typewriter");

    let index = 0;
    function typeWriterEffect() {
        if (index < welcomeText.length) {
            welcomeElement.textContent += welcomeText.charAt(index);
            index++;
            setTimeout(typeWriterEffect, 65);
        }
    }
    typeWriterEffect();

    // 2. Gráfica Circular
    const ctx = document.getElementById("homePieChart").getContext("2d");
    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Sueño Óptimo (55%)", "Cardio (25%)", "Reacción PVT (15%)", "SpO2 (5%)"],
            datasets: [{
                data: [55, 25, 15, 5],
                backgroundColor: ["#3b82f6", "#6366f1", "#0ea5e9", "#38bdf8"],
                borderWidth: 2,
                borderColor: "#1e293b"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: { color: "#94a3b8", font: { size: 11, weight: "600" }, boxWidth: 12 }
                }
            }
        }
    });

    // 3. Conectar con datos reales desde Python si está activo
    const pythonData = await PythonBridge.fetchHomeData(subject);
    if (pythonData) {
        if (pythonData.ai_advice) {
            document.getElementById("py-home-ai-advice").innerHTML = `<strong class="text-blue-400">Little AI Advice:</strong> ${pythonData.ai_advice}`;
        }
        if (pythonData.missions) {
            document.getElementById("py-home-missions").innerText = pythonData.missions;
        }
    }
});
