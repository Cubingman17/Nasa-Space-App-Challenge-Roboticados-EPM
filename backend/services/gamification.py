from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from models.tables import Astronaut, GamificationProfile
except ModuleNotFoundError:
    from backend.models.tables import Astronaut, GamificationProfile


def _get_state(db: Session, astronaut_id: str) -> GamificationProfile:
    state = db.get(GamificationProfile, astronaut_id)
    if state is None:
        if db.get(Astronaut, astronaut_id) is None:
            db.add(Astronaut(id=astronaut_id))
            db.flush()
        state = GamificationProfile(astronaut_id=astronaut_id)
        db.add(state)
        db.flush()
    return state


def award_assessment(db: Session, astronaut_id: str, payload: dict, overall_status: str) -> dict:
    """Award the same log/sleep/reaction rewards as the existing app."""
    state = _get_state(db, astronaut_id)
    points, xp = 2, 10
    sleep = float(payload["sleep_hours"])
    reaction = float(payload["rt_ms"])
    if sleep > 7:
        points += 3
        xp += 15
    if reaction < 300:
        points += 3
        xp += 15

    state.points += points
    state.xp += xp
    today = datetime.now(timezone.utc).date()
    today_text = today.isoformat()
    if state.last_log_date != today_text:
        yesterday = (today - timedelta(days=1)).isoformat()
        state.streak = state.streak + 1 if state.last_log_date == yesterday else 1
        state.last_log_date = today_text
    state.zstate = {
        "normal": "Optimal (Z < 1.5)",
        "atention": "Moderate Alert (Z 1.5 - 2.5)",
        "bad": "Critical Alert (Z > 2.5)",
        "critical": "Critical Alert (Z > 2.5)",
    }.get(overall_status, "Unknown")
    return {"earned_points": points, "earned_xp": xp, **serialize_state(state)}


def serialize_state(state: GamificationProfile | None) -> dict:
    if state is None:
        return {"points": 0, "xp": 0, "streak": 0, "last_log_date": None, "zstate": None}
    return {
        "points": state.points,
        "xp": state.xp,
        "streak": state.streak,
        "last_log_date": state.last_log_date,
        "zstate": state.zstate,
    }


def get_state(db: Session, astronaut_id: str) -> dict:
    return serialize_state(db.get(GamificationProfile, astronaut_id))


def get_ranking(db: Session, limit: int = 100) -> list[dict]:
    rows = db.execute(
        select(Astronaut, GamificationProfile)
        .join(GamificationProfile, GamificationProfile.astronaut_id == Astronaut.id)
        .order_by(GamificationProfile.points.desc(), GamificationProfile.xp.desc(), Astronaut.id)
        .limit(limit)
    ).all()
    return [
        {"astronaut_id": astronaut.id, "name": astronaut.name or astronaut.id, **serialize_state(state)}
        for astronaut, state in rows
    ]
