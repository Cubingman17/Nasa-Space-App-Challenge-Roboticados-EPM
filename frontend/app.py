"""Native Streamlit interface for AstroHealth AI.

Run from the repository root with ``streamlit run frontend/app.py``. The
FastAPI service is started locally on port 5000 when it is not already up.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
API_ROOT = os.environ.get("ASTROHEALTH_API_URL", "http://127.0.0.1:5000/api").rstrip("/")
PAGE_NAMES = ["Home", "Data", "AstroAI", "Profile"]
CATEGORY_NAMES = {
    "radiation": "Radiation",
    "microgravity": "Microgravity",
    "psychology": "Psychology",
    "environment": "Environment",
}

st.set_page_config(
    page_title="AstroHealth AI | NASA Space Apps",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #07111f; color: #e5edf7; }
    [data-testid="stSidebar"] { background: #0b1627; border-right: 1px solid #1e293b; }
    [data-testid="stMetric"] { background: #101d30; padding: 1rem; border: 1px solid #24344b; border-radius: 14px; }
    .hero { padding: 1.3rem 1.5rem; border: 1px solid #24344b; border-radius: 18px; background: linear-gradient(120deg,#10223a,#0b1627); margin-bottom: 1rem; }
    .muted { color: #94a3b8; }
    div[data-testid="stExpander"] { border: 1px solid #25354c; border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


class APIError(RuntimeError):
    pass


def api_request(method: str, path: str, *, params: dict | None = None, body: dict | None = None):
    url = f"{API_ROOT}{path}"
    if params:
        url += "?" + urlencode(params)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as error:
        try:
            detail = json.loads(error.read().decode("utf-8")).get("detail", str(error))
        except (ValueError, AttributeError):
            detail = str(error)
        raise APIError(f"API {error.code}: {detail}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise APIError(f"No se pudo conectar con el backend: {error}") from error


@st.cache_resource
def start_backend() -> dict:
    """Reuse a running API or start the bundled FastAPI app.

    A subprocess is used instead of an in-process thread: the backend mixes
    'backend.*' and plain module imports, and when Streamlit runs from the
    repository root both styles become importable at once, which makes
    SQLAlchemy declare its tables twice and crash. A subprocess gets a clean
    sys.path, exactly like running uvicorn inside backend/.
    """
    try:
        api_request("GET", "/health")
        return {"status": "running", "server": None, "thread": None}
    except APIError:
        pass

    import subprocess
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    try:
        import uvicorn
        from backend.main import app as api_app

    try:
        process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn", "main:app",
                "--host", "127.0.0.1", "--port", "5000",
            ],
            cwd=str(BACKEND_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as error:
        return {"status": "error", "server": None, "thread": None, "error": str(error)}

    for _ in range(50):
        if process.poll() is not None:
            return {
                "status": "error",
                "server": None,
                "thread": None,
                "error": "The backend process exited immediately. Run it manually to see the error: cd backend && uvicorn main:app --port 5000",
            }
        try:
            api_request("GET", "/health")
            return {"status": "running", "server": process, "thread": None}
        except APIError:
            time.sleep(0.2)
    return {"status": "error", "server": None, "thread": None, "error": "FastAPI did not respond on port 5000."}


backend = start_backend()


def show_api_error(error: Exception) -> None:
    st.error(str(error))


def load_profiles() -> list[dict]:
    try:
        return api_request("GET", "/profiles").get("profiles", [])
    except APIError:
        return []


profiles = load_profiles() if backend["status"] == "running" else []
profile_ids = [profile["astronaut_id"] for profile in profiles]
default_subject = st.session_state.get("subject_id")
if default_subject not in profile_ids:
    default_subject = profile_ids[0] if profile_ids else "AST-001"

with st.sidebar:
    logo = ROOT_DIR / "frontend" / "Logo_NASA.webp"
    if logo.exists():
        st.image(str(logo), width=92)
    st.title("AstroHealth AI")
    st.caption("NASA Space Apps Challenge · Roboticados EPM")
    page = st.radio("Navegación", PAGE_NAMES, horizontal=False)
    if profile_ids:
        selected_index = profile_ids.index(default_subject) if default_subject in profile_ids else 0
        subject_id = st.selectbox(
            "Astronauta activo",
            profile_ids,
            index=selected_index,
            format_func=lambda item: next(
                (p["name"] for p in profiles if p["astronaut_id"] == item), item
            ),
        )
    else:
        subject_id = st.text_input("Astronauta activo", value=default_subject)
    st.session_state["subject_id"] = subject_id
    if backend["status"] == "running":
        st.success("Backend conectado · FastAPI :5000")
    else:
        st.error("Backend sin conexión")
        st.caption(backend.get("error", "Revisa las dependencias de requirements.txt."))


def render_home() -> None:
    st.markdown(
        f'<div class="hero"><h1>Welcome, Astronaut {subject_id}</h1>'
        '<p class="muted">Resumen de salud y datos de misión guardados en el backend.</p></div>',
        unsafe_allow_html=True,
    )
    try:
        home = api_request("GET", "/home", params={"subject": subject_id})
    except APIError as error:
        show_api_error(error)
        return

    reading = home.get("latest_assessment")
    vitals = home.get("vitals", {})
    card_columns = st.columns(5)
    cards = [
        ("Heart rate", "bpm", "bpm"),
        ("SpO₂", "spo2_pct", "%"),
        ("Sleep", "sleep_hours", "h"),
        ("Reaction", "reaction_time_ms", "ms"),
    ]
    metric_values = reading.get("metrics", {}) if reading else {}
    for column, (label, vital_key, unit) in zip(card_columns, cards):
        value = vitals.get(vital_key, {}).get("value")
        if value is None:
            source_key = {"bpm": "bpm", "spo2_pct": "spO2", "sleep_hours": "sleep", "reaction_time_ms": "reaction"}[vital_key]
            value = metric_values.get(source_key, {}).get("value")
        column.metric(label, f"{value} {unit}" if value is not None else "No data")
    fatigue = metric_values.get("fatigue", {}).get("value") if metric_values else None
    card_columns[4].metric("Fatigue", f"{fatigue} / 10" if fatigue is not None else "Manual input")

    if reading:
        status = reading.get("overall_status", "unknown")
        message = home.get("ai_advice", "")
        if status in {"critical", "bad"}:
            st.error(f"Estado general: {status.upper()} · {message}")
        elif status == "atention":
            st.warning(f"Estado general: {status.upper()} · {message}")
        else:
            st.success(f"Estado general: {status.upper()} · {message}")
    else:
        st.info(home.get("ai_advice", "Aún no hay evaluaciones manuales."))

    st.subheader("Risk indicators from source CSV labels")
    risks = home.get("risk", {})
    risk_cols = st.columns(4)
    for col, category in zip(risk_cols, CATEGORY_NAMES):
        risk = risks.get(category, {})
        col.metric(CATEGORY_NAMES[category], str(risk.get("status", "no_data")).upper())
    progress = home.get("gamification", {})
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Points", progress.get("points", 0))
    col_b.metric("XP", progress.get("xp", 0))
    col_c.metric("Daily streak", progress.get("streak", 0))
    st.caption(
        f"Misión registrada hoy: {home.get('missions', 0)} · "
        f"Observaciones CSV: {home.get('data', {}).get('total_observations', 0)}"
    )
    ranking = home.get("ranking", [])
    if ranking:
        st.subheader("Crew ranking")
        st.dataframe(
            pd.DataFrame(ranking)[["astronaut_id", "name", "points", "xp", "streak"]],
            hide_index=True,
            width="stretch",
        )


def render_data() -> None:
    st.title("Mission Data")
    st.caption("Explora las 32 series CSV agrupadas en las cuatro categorías de datos.")
    try:
        category_data = api_request("GET", "/data").get("categories", [])
    except APIError as error:
        show_api_error(error)
        return
    available = [item for item in category_data if item.get("id") in CATEGORY_NAMES]
    if not available:
        st.info("El catálogo de métricas no está disponible.")
        return
    category_labels = {
        f"{CATEGORY_NAMES[item['id']]} · {item.get('observation_count', 0)} rows": item["id"]
        for item in available
    }
    selected_label = st.radio("Categoría", list(category_labels), horizontal=True)
    category_id = category_labels[selected_label]
    try:
        selected = api_request("GET", f"/data/{category_id}")
    except APIError as error:
        show_api_error(error)
        return
    st.write(selected.get("description", ""))
    st.caption(f"{len(selected.get('metrics', []))} metric datasets · {selected.get('observation_count', 0)} observations")

    for metric in selected.get("metrics", []):
        metric_id = metric["id"]
        try:
            result = api_request(
                "GET",
                f"/data/metrics/{metric_id}/observations",
                params={"astronaut_id": subject_id, "limit": 10000},
            )
        except APIError as error:
            st.error(f"{metric.get('name', metric_id)}: {error}")
            continue
        observations = result.get("observations", [])
        with st.expander(
            f"{metric.get('name', 'Metric')} · {len(observations)} records",
            expanded=True,
        ):
            st.caption(f"{metric.get('description', '')} · Unit: {metric.get('unit', '—')}")
            if not observations:
                st.info("No observations for this astronaut.")
                continue
            rows = []
            for observation in observations:
                rows.append({
                    "timestamp": observation.get("timestamp"),
                    "measurement_id": observation.get("measurement_id"),
                    "astronaut_id": observation.get("astronaut_id"),
                    **observation.get("values", {}),
                })
            frame = pd.DataFrame(rows)
            st.dataframe(frame, hide_index=True, width="stretch")
            numeric_columns = [
                name for name in frame.select_dtypes(include="number").columns
                if name != "measurement_id"
            ]
            if numeric_columns:
                chart = frame[["timestamp", *numeric_columns]].copy()
                chart["timestamp"] = pd.to_datetime(chart["timestamp"], errors="coerce", utc=True)
                chart = chart.dropna(subset=["timestamp"]).set_index("timestamp")
                st.line_chart(chart, height=230, width="stretch")
            else:
                st.caption("This dataset has no numeric series to plot.")
            st.download_button(
                "Download CSV",
                frame.to_csv(index=False).encode("utf-8"),
                file_name=f"{metric.get('dataset_key', metric_id)}.csv",
                mime="text/csv",
                key=f"download-{category_id}-{metric_id}",
            )


def render_ai() -> None:
    st.title("AstroAI · Health assessment")
    st.caption("Enter the five required metrics. Optional fields are evaluated only when provided.")
    with st.form("health_assessment"):
        st.subheader("Core metrics")
        c1, c2, c3 = st.columns(3)
        bpm = c1.number_input("Heart rate (BPM)", min_value=1.0, max_value=250.0, value=70.0)
        spo2 = c2.number_input("SpO₂ (%)", min_value=1.0, max_value=100.0, value=98.0)
        sleep = c3.number_input("Sleep (hours)", min_value=0.0, max_value=24.0, value=8.0)
        c4, c5 = st.columns(2)
        reaction = c4.number_input("Reaction time (ms)", min_value=1.0, max_value=5000.0, value=250.0)
        fatigue = c5.number_input("Fatigue (1–10)", min_value=1.0, max_value=10.0, value=2.0)
        with st.expander("Optional metrics"):
            o1, o2, o3 = st.columns(3)
            glucose = o1.number_input("Glucose (mg/dL)", min_value=0.0, value=0.0, help="Leave at 0 to omit.")
            systolic = o2.number_input("Systolic BP (mmHg)", min_value=0.0, value=0.0, help="Leave at 0 to omit.")
            diastolic = o3.number_input("Diastolic BP (mmHg)", min_value=0.0, value=0.0, help="Leave at 0 to omit.")
            o4, o5, o6 = st.columns(3)
            temp = o4.number_input("Body temperature (°C)", min_value=0.0, value=0.0, help="Leave at 0 to omit.")
            mood = o5.number_input("Mood (1–10)", min_value=0.0, value=0.0, help="Leave at 0 to omit.")
            radiation = o6.number_input("Radiation (µSv)", min_value=0.0, value=0.0, help="Leave at 0 to omit.")
            co2 = st.number_input("Cabin CO₂ (ppm)", min_value=0.0, value=0.0, help="Leave at 0 to omit.")
        submitted = st.form_submit_button("Analyze and save", type="primary", width="stretch")
    if submitted:
        payload = {
            "subject_id": subject_id,
            "hr_bpm": bpm,
            "spo2_pct": spo2,
            "sleep_hours": sleep,
            "rt_ms": reaction,
            "fatigue_level": fatigue,
        }
        optional = {
            "blood_glucose": glucose,
            "bp_systolic": systolic,
            "bp_diastolic": diastolic,
            "body_temp_c": temp,
            "mood_level": mood,
            "radiation_usv": radiation,
            "cabin_co2": co2,
        }
        payload.update({key: value for key, value in optional.items() if value > 0})
        try:
            result = api_request("POST", "/predict", body=payload)
            st.session_state["last_ai_result"] = result
            st.success(f"Assessment saved · Overall status: {result['overall_status'].upper()}")
        except (APIError, KeyError) as error:
            show_api_error(error)

    last_result = st.session_state.get("last_ai_result")
    if last_result and last_result.get("subject_id") == subject_id:
        st.subheader("Latest assessment")
        metrics = last_result.get("metrics", {})
        columns = st.columns(min(5, max(1, len(metrics))))
        for index, metric in enumerate(metrics.values()):
            columns[index % len(columns)].metric(
                metric.get("label", "Metric"),
                f"{metric.get('value')} {metric.get('unit', '')}",
                metric.get("status", ""),
            )
        st.write(last_result.get("ai_response", ""))

    st.divider()
    st.subheader("Chat with AstroAI")
    history_key = f"chat-{subject_id}"
    history = st.session_state.setdefault(history_key, [])
    for item in history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    prompt = st.chat_input("Ask about your latest assessment")
    if prompt:
        history.append({"role": "user", "content": prompt})
        try:
            reply = api_request("POST", "/chat", body={"prompt": prompt, "subject_id": subject_id})
            answer = reply.get("reply", "No response returned.")
            history.append({"role": "assistant", "content": answer})
            st.rerun()
        except APIError as error:
            show_api_error(error)


def render_profile() -> None:
    st.title("Astronaut profile")
    try:
        profile = api_request("GET", f"/profile/{subject_id}")
    except APIError as error:
        profile = None
        st.info("Create a profile below to get started.")
    if profile:
        st.subheader(profile.get("name", subject_id))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Points", profile.get("points", 0))
        c2.metric("XP", profile.get("xp", 0))
        c3.metric("Level", profile.get("level", 1))
        c4.metric("Streak", profile.get("streak", 0))
        with st.form("edit_profile"):
            name = st.text_input("Name", value=profile.get("name", ""))
            c1, c2, c3 = st.columns(3)
            age = c1.number_input("Age", min_value=0, max_value=120, value=int(profile.get("age") or 20))
            height = c2.number_input("Height (cm)", min_value=0.0, value=float(profile.get("height_cm") or 170.0))
            weight = c3.number_input("Weight (kg)", min_value=0.0, value=float(profile.get("weight_kg") or 70.0))
            save = st.form_submit_button("Save profile", type="primary")
        if save:
            data = {"name": name.strip(), "age": age}
            if height > 0:
                data["height_cm"] = height
            if weight > 0:
                data["weight_kg"] = weight
            try:
                api_request("PUT", f"/profile/{subject_id}", body=data)
                st.success("Profile saved.")
                st.rerun()
            except APIError as error:
                show_api_error(error)
        st.write("Badges:", ", ".join(profile.get("badges", [])) or "No badges yet")
        st.caption(f"Latest assessment status: {profile.get('latest_status') or 'No assessment yet'}")

    with st.expander("Add an astronaut profile"):
        with st.form("new_profile"):
            new_id = st.text_input("Astronaut ID", placeholder="e.g. AST-002")
            new_name = st.text_input("Name")
            create = st.form_submit_button("Create profile")
        if create:
            if not new_id.strip() or not new_name.strip():
                st.warning("Enter both an astronaut ID and a name.")
            else:
                try:
                    api_request("PUT", f"/profile/{new_id.strip()}", body={"name": new_name.strip()})
                    st.session_state["subject_id"] = new_id.strip()
                    st.success("Profile created. Select it in the sidebar.")
                    st.rerun()
                except APIError as error:
                    show_api_error(error)

    try:
        ranking = api_request("GET", "/ranking").get("ranking", [])
        if ranking:
            st.subheader("Crew ranking")
            st.dataframe(pd.DataFrame(ranking), hide_index=True, width="stretch")
    except APIError as error:
        show_api_error(error)


if backend["status"] != "running":
    st.warning("No se pueden cargar las pantallas hasta que el backend esté disponible.")
elif page == "Home":
    render_home()
elif page == "Data":
    render_data()
elif page == "AstroAI":
    render_ai()
else:
    render_profile()
