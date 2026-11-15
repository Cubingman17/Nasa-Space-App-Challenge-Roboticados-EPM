// Base de datos completamente independiente para cada usuario (Foto, Peso, Altura, Edad, etc.)
const profilesDatabase = {
    A: {
        name: "Persona A",
        weight: "70 kg",
        height: "175 cm",
        age: "20 años",
        hr: "68 bpm",
        avatar: "👨‍🚀",
        score: "110 XP (8 pts)",
        streak: "3 Días",
        zstate: "Óptimo (Z < 1.5)"
    },
    B: {
        name: "Persona B",
        weight: "65 kg",
        height: "168 cm",
        age: "21 años",
        hr: "72 bpm",
        avatar: "👩‍🚀",
        score: "95 XP (6 pts)",
        streak: "1 Día",
        zstate: "Alerta Moderada"
    },
    C: {
        name: "Persona C",
        weight: "78 kg",
        height: "180 cm",
        age: "19 años",
        hr: "64 bpm",
        avatar: "🧑‍🚀",
        score: "125 XP (10 pts)",
        streak: "4 Días",
        zstate: "Excelente (Z < 1.0)"
    }
};

function updateProfileSubject(subjectId) {
    localStorage.setItem("selectedSubject", subjectId);
    const data = profilesDatabase[subjectId];
    if (!data) return;

    // Actualizar campos de perfil independientes
    document.getElementById("py-prof-weight").innerText = data.weight;
    document.getElementById("py-prof-height").innerText = data.height;
    document.getElementById("py-prof-age").innerText = data.age;
    document.getElementById("py-prof-hr").innerText = data.hr;
    
    document.getElementById("profile-avatar-box").innerText = data.avatar;
    document.getElementById("profile-avatar-label").innerText = `SUJETO ${subjectId}`;
    
    document.getElementById("py-profile-name-title").innerText = data.name;
    document.getElementById("py-prof-score").innerText = data.score;
    document.getElementById("py-prof-streak").innerText = data.streak;
    document.getElementById("py-prof-zstate").innerText = data.zstate;

    // Actualizar el selector en caso de recarga
    const selector = document.getElementById("py-subject-select");
    if (selector) selector.value = subjectId;
}

document.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("selectedSubject") || "A";
    updateProfileSubject(saved);
});
