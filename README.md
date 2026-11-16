# AstroHealth AI — Astronaut Health Monitoring Software
https://youtu.be/GDXZor_ry4E

**NASA Space Apps Challenge 2026** — *Create Health Monitoring Software for Astronauts on Space Missions*

## Short Description (submission summary)

> AstroHealth AI is a health monitoring console for astronauts on long-duration missions. It gathers vital signs (BPM, SpO2, sleep, reaction time, fatigue) plus optional metrics (blood glucose, blood pressure, body temperature, mood, radiation, cabin CO2), evaluates them against clinical thresholds, and surfaces the five NASA spaceflight hazards: radiation, isolation and confinement, altered gravity, hostile environment, and distance. A fully local AI companion (Ollama, no cloud) turns the numbers into plain-language guidance and emotional support, so the crew can evaluate and act on their health autonomously, millions of kilometers from Earth.

## The Problem

Long-duration missions expose astronauts to five recognized spaceflight hazards: **space radiation, isolation and confinement, altered gravity, a hostile closed environment, and distance from Earth**. On a Mars-class mission, there is no real-time ground support: the crew must gather health indicators, evaluate their own status, and act on it autonomously.

## What We Built

AstroHealth AI is a tablet-style mission console with four screens:

- **HOME** — mission dashboard with live health status (green / yellow / red) and AI advice.
- **DATA** — the five NASA hazards with pre-flight / in-flight / post-flight comparisons (NASA LSDA & OSDR datasets), plus a manual sensor & log entry form. Required metrics: BPM, SpO2, sleep hours, reaction time (PVT), fatigue level. Optional: blood glucose, blood pressure, body temperature, mood, radiation dose, cabin CO2, cabin temperature, weight, notes.
- **AI** — a local LLM companion ("AstroAI", built on Ollama) that analyzes the latest metrics and answers in plain language, with an emotional-support persona for isolation and confinement. Works fully offline; no data leaves the spacecraft.
- **PROFILE** — astronaut profile with photo upload, XP score, logging streak, and crew gamification ranking (bonuses for sleep > 7 h, reaction < 300 ms, first to log).

### How it maps to the challenge (gather → evaluate → act)

1. **Gather** — the crew logs required + optional metrics through the DATA screen (manual entry today, sensor-ready payload).
2. **Evaluate** — a rule-based engine (`backend/ai/ia.py`) classifies every metric as `normal / atention / bad / critical` using documented clinical thresholds, and computes an overall worst-case status.
3. **Act** — the local AI companion translates the evaluation into concrete guidance and emotional support, and the console UI (status border, banners, ranking) nudges the crew toward healthy behavior.

## Architecture

```
index.html          Web console entry point (HOME)
frontend/           HTML/JS/CSS client assets (DATA, AI, PROFILE screens)
backend/            FastAPI server (port 5000) - also serves the web console
├── routers/         /api/predict, /api/chat, /api/data, /api/home, /api/profile
├── ai/
│   ├── ia.py            Rule-based metric evaluators (69 unit tests)
│   ├── metrics_reader.py  Payload parsing + AI response + suggestions builder
│   ├── local_llm.py      Ollama client (localhost:11434)
│   ├── Modelfile         AstroAI custom model (llama3.2:3b base)
│   └── setup_ollama.py   One-command model setup
├── services/        Persistence, gamification, dataset import
└── data/datasets/   32 metric datasets (NASA LSDA & OSDR based)
setup.sh / setup.bat  One-command local installation
```

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic, SQLite (SQLAlchemy)
- **AI:** Ollama with a custom `astroai` model (llama3.2:3b base, health + emotional-support system prompt), 100% local — with a rule-based fallback when Ollama is not running
- **Frontend:** HTML/JS/CSS (vanilla, Chart.js), served by the same FastAPI server
- **Data:** NASA LSDA / OSDR public datasets for hazard context

## How to Run

### Quick start (local, full experience)

**Step 1 - install (once):**

```bash
./setup.sh      # Linux / macOS / Git Bash on Windows
```
```bat
setup.bat       # Windows (CMD / PowerShell)
```

This creates a `.venv` with the dependencies, sets up the local AI model
(optional) and imports the 32 metric datasets.

**Step 2 - run the app (two things):**

1. Start the backend from the repo root:

   ```bash
   python backend/main.py
   ```

2. Open the web console in your browser:

   - **http://localhost:5000** (recommended - the backend serves the whole
     console: HOME, DATA, AI, PROFILE), or
   - open `index.html` (repo root) directly as a file.

The local AI companion (AstroAI) needs [Ollama](https://ollama.com/download);
without it the app still works using the rule-based evaluation and a
metrics-summary fallback, and the UI clearly marks the AI as offline.

### Online demo (GitHub Pages)

The static web console is hosted on GitHub Pages from this same repository.
In that mode the UI is fully browsable (profiles, hazards, gamification and
manual logging with local storage), and any feature that needs the backend
shows an explicit offline notice instead of faking data. The backend and the
local AI model only run on your machine — GitHub Pages is static-only.

To host it yourself: GitHub repo → **Settings → Pages → Source: Deploy from
a branch → main / (root)**. `index.html` at the repo root is the entry point.

### Manual run (no scripts)

```bash
python -m venv .venv && .venv/Scripts/activate   # or source .venv/bin/activate
python -m pip install -r requirements.txt
cd backend/ai && python setup_ollama.py           # optional: local AI model
cd backend && python -m services.import_datasets  # load the 32 datasets
python backend/main.py   # starts the API + console on http://localhost:5000
# open http://localhost:5000 (or index.html in your browser)
```

## Super Intelligence (SI) Disclosure

Per NASA Space Apps 2026 rules, this project includes a description of how
SI tools (Mistral Vibe, Gemini, Claude, ChatGPT) were used during
development: see [SI_DISCLOSURE.md](SI_DISCLOSURE.md).

## Testing

```bash
cd backend
python -m ai.test_ai   # 69 checks: metric thresholds, API endpoints, local LLM
```

## Team

Roboticados EPM — NASA Space Apps Challenge 2026.

---

*Educational prototype built on public NASA datasets and simulated sensors. Not a medical device.*
