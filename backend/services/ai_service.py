from datetime import datetime, timezone

from sqlalchemy.orm import Session

try:
    from ai import local_llm
    from ai.metrics_reader import read_metrics
    from models.tables import Astronaut, HealthAssessment
    from services.gamification import award_assessment
    from services.health_data import latest_assessment
except ModuleNotFoundError:
    from backend.ai import local_llm
    from backend.ai.metrics_reader import read_metrics
    from backend.models.tables import Astronaut, HealthAssessment
    from backend.services.gamification import award_assessment
    from backend.services.health_data import latest_assessment


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
