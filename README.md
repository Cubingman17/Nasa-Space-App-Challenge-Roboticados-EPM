# AstroHealth AI — Astronaut Health Monitoring Software

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
frontend/app.py      Native Streamlit interface (Home, Data, AstroAI, Profile)
frontend/            Existing HTML/JS client assets
backend/             FastAPI (port 5000)
├── routers/         /api/predict, /api/chat, data, profile, home
├── ai/
│   ├── ia.py            Rule-based metric evaluators (62 unit tests)
│   ├── metrics_reader.py  Payload parsing + AI response builder
│   ├── local_llm.py      Ollama client (localhost:11434)
│   ├── Modelfile         AstroAI custom model (llama3.2:3b base)
│   └── setup_ollama.py   One-command model setup
```

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic
- **AI:** Ollama with a custom `astroai` model (llama3.2:3b base, health + emotional-support system prompt), 100% local
- **Frontend:** Streamlit (Python), with the FastAPI backend for persistent data and analysis
- **Data:** NASA LSDA / OSDR public datasets for hazard context

## How to Run

**Option A — one command with Streamlit (recommended for demo):**

```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```

This opens the native Streamlit application at `http://localhost:8501`. It starts the FastAPI backend on port 5000 when one is not already running. The Data screen reads the 32 CSV-backed metric datasets from the API; AstroAI and Profile use the same persistent backend.

**Option B — backend + static frontend separately:**

1. Set up the local AI model:
   ```bash
   cd backend/ai
   python setup_ollama.py   # pulls llama3.2:3b and creates the astroai model
   ```
2. Start the backend:
   ```bash
   cd backend
   uvicorn main:app --port 5000
   ```
3. Open `frontend/index.html` in the browser.

> Note: on Streamlit Community Cloud the UI renders as a visual demo; the live backend and the local Ollama model only work when running locally.

## Super Intelligence (SI) Disclosure

Per NASA Space Apps 2026 rules, this project includes a description of how
SI tools (Mistral Vibe, Gemini, Claude, ChatGPT) were used during
development: see [SI_DISCLOSURE.md](SI_DISCLOSURE.md).

## Testing

```bash
cd backend
python -m ai.test_ai   # 65 checks: metric thresholds, API endpoints, local LLM
```

## Team

Roboticados EPM — NASA Space Apps Challenge 2026.

---

*Educational prototype built on public NASA datasets and simulated sensors. Not a medical device.*
