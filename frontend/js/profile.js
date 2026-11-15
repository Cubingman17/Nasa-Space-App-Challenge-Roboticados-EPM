const subjectsProfile = {
    A: { weight: "70 kg", height: "175 cm", age: "20 años", hr: "68 bpm" },
    B: { weight: "65 kg", height: "168 cm", age: "21 años", hr: "72 bpm" },
    C: { weight: "78 kg", height: "180 cm", age: "19 años", hr: "64 bpm" }
};

function updateProfileSubject(subjectId) {
    localStorage.setItem("selectedSubject", subjectId);
    const data = subjectsProfile[subjectId];
    if (!data) return;

    document.getElementById("py-prof-weight").innerText = data.weight;
    document.getElementById("py-prof-height").innerText = data.height;
    document.getElementById("py-prof-age").innerText = data.age;
    document.getElementById("py-prof-hr").innerText = data.hr;
}

document.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("selectedSubject") || "A";
    document.getElementById("py-subject-select").value = saved;
    updateProfileSubject(saved);
});
