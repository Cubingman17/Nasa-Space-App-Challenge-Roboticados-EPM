// Profile screen: renders the selected astronaut from the shared store
// (js/profiles.js) and manages profiles (rename, add, remove, edit data).

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
        const profile = getProfile(subjectId);
        box.innerText = profile ? profile.avatar : "👨‍🚀";
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
            const subject = getSelectedSubject();
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

function populateSubjectSelector() {
    const selector = document.getElementById("py-subject-select");
    if (!selector) return;

    const current = getSelectedSubject();
    selector.innerHTML = "";
    loadProfiles().forEach((profile) => {
        const option = document.createElement("option");
        option.value = profile.id;
        option.innerText = profile.name;
        selector.appendChild(option);
    });
    selector.value = current;
}

function renderRanking() {
    const container = document.getElementById("py-profile-ranking");
    if (!container) return;

    const ranking = computeRanking();
    const medals = ["1ST", "2ND", "3RD", "4TH", "5TH", "6TH", "7TH", "8TH"];
    const selected = getSelectedSubject();

    let rows = "";
    ranking.forEach((profile, index) => {
        const highlight = profile.id === selected ? "text-blue-300" : "text-slate-300";
        rows += `<div class="flex justify-between items-center text-xs md:text-sm font-bold border-b border-slate-800 pb-1.5 ${highlight}">
            <span>${medals[index] || (index + 1) + "TH"} : ${escapeHtml(profile.name)}</span>
            <span class="flex items-center gap-2">
                <span class="text-amber-400" title="${profile.streak || 0} day logging streak">&#128293; ${profile.streak || 0}d</span>
                <span class="text-blue-400 font-extrabold">${profile.points} pts</span>
            </span>
        </div>`;
    });

    container.innerHTML = `
        <h4 class="font-bold text-xs uppercase text-slate-400">Points Ranking</h4>
        ${rows}
    `;
}

function updateProfileSubject(subjectId) {
    setSelectedSubject(subjectId);
    const profile = getProfile(subjectId);
    if (!profile) return;

    document.getElementById("py-prof-weight").innerText = `${profile.weight} kg`;
    document.getElementById("py-prof-height").innerText = `${profile.height} cm`;
    document.getElementById("py-prof-age").innerText = `${profile.age} years`;
    document.getElementById("py-prof-hr").innerText = `${profile.hrBaseline} bpm`;

    renderAvatar(subjectId);
    document.getElementById("profile-avatar-label").innerText = `SUBJECT ${subjectId}`;

    document.getElementById("py-profile-name-title").innerText = profile.name;
    document.getElementById("py-prof-score").innerText = `${profile.xp} XP (${profile.points} pts)`;
    document.getElementById("py-prof-streak").innerText = `${profile.streak} Day${profile.streak === 1 ? "" : "s"}`;
    document.getElementById("py-prof-zstate").innerText = profile.zstate || "Optimal (Z < 1.5)";

    const selector = document.getElementById("py-subject-select");
    if (selector) selector.value = subjectId;

    renderRanking();
}

// --- Profile management -------------------------------------------------

function renameProfile() {
    const subjectId = getSelectedSubject();
    const profile = getProfile(subjectId);
    if (!profile) return;

    const name = prompt("New name for this astronaut:", profile.name);
    if (!name || !name.trim() || name.trim() === profile.name) return;

    const profiles = loadProfiles();
    profiles.find(p => p.id === subjectId).name = name.trim();
    saveProfiles(profiles);

    populateSubjectSelector();
    updateProfileSubject(subjectId);
}

function addProfile() {
    const name = prompt("Name of the new astronaut:");
    if (!name || !name.trim()) return;

    const profiles = loadProfiles();
    const id = "P" + Date.now().toString(36).toUpperCase();
    const avatars = ["👨‍🚀", "👩‍🚀", "🧑‍🚀", "👩‍🔬", "🧑‍🔬", "👨‍🔬"];
    profiles.push({
        id: id,
        name: name.trim(),
        avatar: avatars[profiles.length % avatars.length],
        weight: 70, height: 170, age: 20, hrBaseline: 70,
        xp: 0, points: 0, streak: 0, lastLogDate: null
    });
    saveProfiles(profiles);

    populateSubjectSelector();
    updateProfileSubject(id);
}

function removeProfile() {
    const profiles = loadProfiles();
    if (profiles.length <= 1) {
        alert("You cannot remove the last profile.");
        return;
    }

    const subjectId = getSelectedSubject();
    const profile = getProfile(subjectId);
    if (!confirm(`Remove "${profile.name}" and all their progress?`)) return;

    const remaining = profiles.filter(p => p.id !== subjectId);
    saveProfiles(remaining);
    try {
        localStorage.removeItem(profilePhotoKey(subjectId));
    } catch (error) {
        // storage unavailable
    }

    populateSubjectSelector();
    updateProfileSubject(remaining[0].id);
}

function editBasicData() {
    const subjectId = getSelectedSubject();
    const profiles = loadProfiles();
    const profile = profiles.find(p => p.id === subjectId);
    if (!profile) return;

    const weight = prompt("Weight (kg):", profile.weight);
    if (weight === null) return;
    const height = prompt("Height (cm):", profile.height);
    if (height === null) return;
    const age = prompt("Age (years):", profile.age);
    if (age === null) return;
    const hr = prompt("Resting HR baseline (bpm):", profile.hrBaseline);
    if (hr === null) return;

    profile.weight = parseFloat(weight) || profile.weight;
    profile.height = parseFloat(height) || profile.height;
    profile.age = parseInt(age, 10) || profile.age;
    profile.hrBaseline = parseInt(hr, 10) || profile.hrBaseline;
    saveProfiles(profiles);

    updateProfileSubject(subjectId);
}

document.addEventListener("DOMContentLoaded", () => {
    populateSubjectSelector();
    updateProfileSubject(getSelectedSubject());
});
