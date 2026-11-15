# Super Intelligence (SI) Tools Disclosure

In accordance with the NASA Space Apps Challenge 2026 guidelines, the use of
Super Intelligence (SI) tools is permitted to accelerate innovation and
creativity, and **each team's project submission must include a description
of how SI tools were used during the development of the project**.

Team **Roboticados EPM** discloses the following SI usage for
**AstroHealth AI** (challenge: *Create Health Monitoring Software for
Astronauts on Space Missions*):

## SI tools used during development

| Tool | Type | How it was used |
|------|------|-----------------|
| **Mistral Vibe** (Mistral AI coding agent) | Code generation agent | Developed the backend metric evaluation engine (`backend/ai/ia.py`), the FastAPI endpoints (`/api/predict`, `/api/chat`, `/api/home`), the 62 unit tests (`backend/ai/test_ai.py`), the frontend integration (forms, hazard cards, API bridge), the local Ollama model setup (`backend/ai/Modelfile`, `setup_ollama.py`), the Streamlit deployment wrapper, and project documentation. |
| **Google Gemini** | Large language model | Research on the challenge statement, the five NASA spaceflight hazards, and the public NASA OSDR / LSDA datasets used as context for the DATA screen. |
| **Claude** (Anthropic) | Large language model | Review and discussion of the clinical threshold ranges used by the metric evaluators (BPM, SpO2, sleep, reaction time, fatigue, glucose, blood pressure). |
| **ChatGPT** (OpenAI) | Large language model | English copywriting for the user interface, help drafting the project description and presentation talking points. |

## SI running inside the solution

AstroHealth AI itself includes an SI component: a fully **local** AI
companion ("AstroAI", a custom [Ollama](https://ollama.com) model built on
llama3.2:3b with a health + emotional-support system prompt). It runs
on-device, requires no internet connection and no data leaves the
spacecraft — a deliberate design choice for deep-space autonomy. Its role is
to translate evaluated metrics into plain-language guidance and emotional
support for the crew.

## Human contribution

All architectural decisions, metric thresholds, dataset selection, product
design, and final review were made by the team. SI output was always
reviewed, tested (62 automated tests) and edited by the team before being
included in the project.

---

*Sources: NASA Space Apps Challenge — Participant FAQs and Project Submission
Guide (spaceappschallenge.org), which ask: "Did you utilize any Super
Intelligence (SI) tools and software in preparing your solution?"*
