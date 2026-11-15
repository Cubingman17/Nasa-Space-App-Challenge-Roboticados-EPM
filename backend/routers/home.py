from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from database import get_db
    from models.tables import HealthAssessment
    from services.gamification import get_ranking, get_state
    from services.health_data import data_summary, latest_assessment, latest_csv_vitals
    from services.risk import category_risk
except ModuleNotFoundError:
    from backend.database import get_db
    from backend.models.tables import HealthAssessment
    from backend.services.gamification import get_ranking, get_state
    from backend.services.health_data import data_summary, latest_assessment, latest_csv_vitals
    from backend.services.risk import category_risk

router = APIRouter(prefix="/api", tags=["Home"])


@router.get("/home")
def home_data(subject: str = "A", db: Session = Depends(get_db)) -> dict:
    assessment = latest_assessment(db, subject)
    summary = data_summary(db, subject)
    state = get_state(db, subject)
    today = datetime.now(timezone.utc).date()
    has_logged_today = db.scalar(
        select(HealthAssessment.id)
        .where(
            HealthAssessment.astronaut_id == subject,
            HealthAssessment.recorded_at >= datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc),
        )
        .limit(1)
    ) is not None
    return {
        "subject": subject,
        "ai_advice": assessment["ai_response"] if assessment else "No metrics registered yet. Log your data in the DATA tab.",
        "missions": 1 if has_logged_today else 0,
        "latest_assessment": assessment,
        "vitals": latest_csv_vitals(db, subject),
        "risk": category_risk(db, subject),
        "gamification": state,
        "ranking": get_ranking(db),
        "data": summary,
    }
