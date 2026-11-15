import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

try:
    from ai import local_llm
    from ai.metrics_reader import read_metrics
    from models.tables import Astronaut, HealthAssessment, Measurement
    from services.gamification import award_assessment
    from services.health_data import latest_assessment
except ModuleNotFoundError:
    from backend.ai import local_llm
    from backend.ai.metrics_reader import read_metrics
    from backend.models.tables import Astronaut, HealthAssessment, Measurement
    from backend.services.gamification import award_assessment
    from backend.services.health_data import latest_assessment


# Manual payload field -> (catalog metric ID, values_json key).
# Mirrors each submitted metric into the catalog tables so the DATA
# screens show the astronaut's own real records.
MANUAL_METRIC_MAP = {
    "hr_bpm": (6, "heart_rate_bpm"),
    "spo2_pct": (26, "spo2_pct"),
    "sleep_hours": (22, "sleep_hours"),
    "rt_ms": (24, "reaction_time_ms"),
    "fatigue_level": (23, "fatigue_level"),
    "blood_glucose": (14, "glucose_mg_dl"),
    "bp_systolic": (3, "systolic_mmhg"),
    "bp_diastolic": (4, "diastolic_mmhg"),
    "body_temp_c": (28, "core_temperature_c"),
    "mood_level": (25, "mood_score"),
    "radiation_usv": (1, "dose_usv"),
    "cabin_co2": (16, "co2_ppm"),
}


def _store_manual_measurements(db: Session, payload: dict, assessment: HealthAssessment) -> None:
    for field, (metric_id, value_key) in MANUAL_METRIC_MAP.items():
        try:
            number = float(payload.get(field))
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            continue
        db.add(Measurement(
            astronaut_id=assessment.astronaut_id,
            metric_id=metric_id,
            record_id=f"manual-{assessment.id}",
            recorded_at=assessment.recorded_at,
            values_json={value_key: number},
            source="manual_entry",
        ))


def analyze(payload: dict, db: Session) -> dict:
    """Evaluate, persist and reward one valid sensor submission."""
    result = read_metrics(payload)
    astronaut_id = str(result.get("subject_id") or "A").strip()
    if not astronaut_id or len(astronaut_id) > 64:
        raise ValueError("subject_id must contain 1 to 64 characters")
    astronaut = db.get(Astronaut, astronaut_id)
    if astronaut is None:
        astronaut = Astronaut(id=astronaut_id)
        db.add(astronaut)
        db.flush()

    assessment = HealthAssessment(
        astronaut_id=astronaut_id,
        recorded_at=datetime.now(timezone.utc),
        overall_status=result["overall_status"],
        metrics_json=result["metrics"],
        input_json={key: value for key, value in payload.items() if key != "subject_id"},
        ai_response=result["ai_response"],
    )
    db.add(assessment)
    db.flush()
    _store_manual_measurements(db, payload, assessment)
    result["gamification"] = award_assessment(
        db, astronaut_id, payload, result["overall_status"]
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    result["assessment_id"] = assessment.id
    result["recorded_at"] = assessment.recorded_at
    return result


def chat(prompt: str, astronaut_id: str, db: Session) -> dict:
    prompt = (prompt or "").strip()
    if not prompt:
        raise ValueError("prompt is required")
    astronaut_id = (astronaut_id or "A").strip()
    reading = latest_assessment(db, astronaut_id)
    context = reading["ai_response"] if reading else "No health assessment has been submitted yet."

    if local_llm.is_available():
        try:
            reply = local_llm.chat(prompt, context)
            if reply:
                return {"reply": reply, "source": "local-llm"}
        except Exception:
            pass

    if reading is None:
        return {
            "reply": "No metrics registered yet. Enter sensor data in the DATA tab before requesting a personalized analysis.",
            "source": "no-data",
        }
    return {"reply": context, "source": "metrics-summary"}
