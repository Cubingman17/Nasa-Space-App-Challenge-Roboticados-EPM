// Shared profile store: each astronaut has their own data, progress and
// ranking. Persisted in localStorage so it survives reloads.

const PROFILES_KEY = "astroProfiles";
const SUBJECT_KEY = "selectedSubject";

const DEFAULT_PROFILES = [
    { id: "A", name: "Person A", avatar: "👨‍🚀", weight: 70, height: 175, age: 20, hrBaseline: 68, xp: 110, points: 8, streak: 3, lastLogDate: null },
    { id: "B", name: "Person B", avatar: "👩‍🚀", weight: 65, height: 168, age: 21, hrBaseline: 72, xp: 95, points: 6, streak: 1, lastLogDate: null },
    { id: "C", name: "Person C", avatar: "🧑‍🚀", weight: 78, height: 180, age: 19, hrBaseline: 64, xp: 125, points: 10, streak: 4, lastLogDate: null }
];

function loadProfiles() {
    try {
        const raw = localStorage.getItem(PROFILES_KEY);
        if (raw) return JSON.parse(raw);
    } catch (error) {
        // storage unavailable: use defaults
    }
    saveProfiles(DEFAULT_PROFILES);
    return DEFAULT_PROFILES;
}

function saveProfiles(profiles) {
    try {
        localStorage.setItem(PROFILES_KEY, JSON.stringify(profiles));
    } catch (error) {
        // storage unavailable: changes live only for this session
    }
}

function getSelectedSubject() {
    const profiles = loadProfiles();
    const saved = localStorage.getItem(SUBJECT_KEY);
    if (saved && profiles.some(p => p.id === saved)) return saved;
    return profiles.length ? profiles[0].id : "A";
}

function setSelectedSubject(subjectId) {
    localStorage.setItem(SUBJECT_KEY, subjectId);
}

function getProfile(subjectId) {
    return loadProfiles().find(p => p.id === subjectId) || null;
}

function profilePhotoKey(subjectId) {
    return `profilePhoto_${subjectId}`;
}

// Z-state label derived from the overall status of the last reading
function zStateFromStatus(status) {
    return {
        normal: "Optimal (Z < 1.5)",
        atention: "Moderate Alert (Z 1.5 - 2.5)",
        bad: "Critical Alert (Z > 2.5)",
        critical: "Critical Alert (Z > 2.5)"
    }[String(status || "normal").split(":")[0].trim()] || "Optimal (Z < 1.5)";
}

// Gamification: called after a successful metrics log for a subject.
// Bonuses: +3 pts / +15 XP for sleeping more than 7 hours and for a
// reaction time under 300 ms. Streak counts consecutive logging days.
function updateProfileProgress(subjectId, payload, response) {
    const profiles = loadProfiles();
    const profile = profiles.find(p => p.id === subjectId);
    if (!profile) return null;

    let earned = 2;
    profile.xp += 10;

    const sleep = parseFloat(payload.sleep_hours);
    const reaction = parseFloat(payload.rt_ms);
    if (!isNaN(sleep) && sleep > 7) { earned += 3; profile.xp += 15; }
    if (!isNaN(reaction) && reaction < 300) { earned += 3; profile.xp += 15; }
    profile.points += earned;

    const today = new Date().toDateString();
    if (profile.lastLogDate !== today) {
        const yesterday = new Date(Date.now() - 86400000).toDateString();
        profile.streak = profile.lastLogDate === yesterday ? profile.streak + 1 : 1;
        profile.lastLogDate = today;
    }

    profile.zstate = zStateFromStatus(response && response.overall_status);
    saveProfiles(profiles);
    return { earned, profile };
}

// Ranking: all profiles sorted by points (ties broken by XP)
function computeRanking() {
    return loadProfiles().slice().sort((a, b) =>
        b.points - a.points || b.xp - a.xp
    );
}

// --- Status helpers shared by all screens -------------------------------

// Color per health status (used by dots, charts and banners)
function statusColor(status) {
    const base = String(status || "normal").split(":")[0].trim();
    return {
        normal: "#10b981",
        atention: "#f59e0b",
        bad: "#f97316",
        critical: "#f43f5e"
    }[base] || "#10b981";
}

// Health score 0-100 per metric status (used by the HOME radar)
function statusScore(status) {
    const base = String(status || "normal").split(":")[0].trim();
    return { normal: 100, atention: 60, bad: 30, critical: 10 }[base] || 100;
}

// Last full reading of a subject (saved by data.js after each log)
function getLastReading(subjectId) {
    try {
        const raw = localStorage.getItem(`lastReading_${subjectId}`);
        return raw ? JSON.parse(raw) : null;
    } catch (error) {
        return null;
    }
}
