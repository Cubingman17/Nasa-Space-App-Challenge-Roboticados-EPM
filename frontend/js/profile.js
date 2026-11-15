// Independent database per user (Photo, Weight, Height, Age, etc.)
const profilesDatabase = {
    A: {
        name: "Person A",
        weight: "70 kg",
        height: "175 cm",
        age: "20 years",
        hr: "68 bpm",
        avatar: "👨‍🚀",
        score: "110 XP (8 pts)",
        streak: "3 Days",
        zstate: "Optimal (Z < 1.5)"
    },
    B: {
        name: "Person B",
        weight: "65 kg",
        height: "168 cm",
        age: "21 years",
        hr: "72 bpm",
        avatar: "👩‍🚀",
        score: "95 XP (6 pts)",
        streak: "1 Day",
        zstate: "Moderate Alert"
    },
    C: {
        name: "Person C",
        weight: "78 kg",
        height: "180 cm",
        age: "19 years",
        hr: "64 bpm",
        avatar: "🧑‍🚀",
        score: "125 XP (10 pts)",
        streak: "4 Days",
        zstate: "Excellent (Z < 1.0)"
    }
};

function profilePhotoKey(subjectId) {
    return `profilePhoto_${subjectId}`;
}

// Shows the saved photo for the subject, or their default avatar emoji
function renderAvatar(subjectId) {
    const box = document.getElementById("profile-avatar-box");
    if (!box) return;

    let photo = null;
    try {
        photo = localStorage.getItem(profilePhotoKey(subjectId));
    } catch (error) {
        // storage unavailable: fall back to the emoji
    }

    if (photo) {
        box.innerHTML = `<img src="${photo}" alt="Profile photo" class="w-full h-full object-cover rounded-full">`;
    } else {
        const data = profilesDatabase[subjectId];
        box.innerText = data ? data.avatar : "👨‍🚀";
    }
}

// Easy photo upload: pick a file, crop it to a 256x256 square and save it
function handleAvatarUpload(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement("canvas");
            canvas.width = 256;
            canvas.height = 256;
            const ctx = canvas.getContext("2d");
            const scale = Math.max(256 / img.width, 256 / img.height);
            const w = img.width * scale;
            const h = img.height * scale;
            ctx.drawImage(img, (256 - w) / 2, (256 - h) / 2, w, h);

            const dataUrl = canvas.toDataURL("image/jpeg", 0.85);
            const subject = localStorage.getItem("selectedSubject") || "A";
            try {
                localStorage.setItem(profilePhotoKey(subject), dataUrl);
                renderAvatar(subject);
            } catch (error) {
                alert("Could not save the photo (storage is full).");
            }
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
    event.target.value = "";
}

function updateProfileSubject(subjectId) {
    localStorage.setItem("selectedSubject", subjectId);
    const data = profilesDatabase[subjectId];
    if (!data) return;

    // Update the independent profile fields
    document.getElementById("py-prof-weight").innerText = data.weight;
    document.getElementById("py-prof-height").innerText = data.height;
    document.getElementById("py-prof-age").innerText = data.age;
    document.getElementById("py-prof-hr").innerText = data.hr;

    renderAvatar(subjectId);
    document.getElementById("profile-avatar-label").innerText = `SUBJECT ${subjectId}`;

    document.getElementById("py-profile-name-title").innerText = data.name;
    document.getElementById("py-prof-score").innerText = data.score;
    document.getElementById("py-prof-streak").innerText = data.streak;
    document.getElementById("py-prof-zstate").innerText = data.zstate;

    // Keep the selector in sync after a reload
    const selector = document.getElementById("py-subject-select");
    if (selector) selector.value = subjectId;
}

document.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("selectedSubject") || "A";
    updateProfileSubject(saved);
});
