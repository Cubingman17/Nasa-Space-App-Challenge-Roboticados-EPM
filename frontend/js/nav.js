document.addEventListener("DOMContentLoaded", () => {
    const savedSubject = localStorage.getItem("selectedSubject") || "A";
    const userLabel = document.getElementById("py-home-user");
    if (userLabel) {
        userLabel.innerText = `ASTRONAUTA ${savedSubject}`;
    }
});