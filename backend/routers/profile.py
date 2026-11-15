import math

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from database import get_db
    from models.tables import Astronaut, GamificationProfile
    from services.gamification import get_ranking, serialize_state
    from services.health_data import latest_assessment
except ModuleNotFoundError:
    from backend.database import get_db
    from backend.models.tables import Astronaut, GamificationProfile
    from backend.services.gamification import get_ranking, serialize_state
    from backend.services.health_data import latest_assessment

router = APIRouter(prefix="/api", tags=["Profile"])
PROFILE_FIELDS = {"name", "age", "height_cm", "weight_kg", "photo_url"}


def _profile_payload(db: Session, astronaut: Astronaut) -> dict:
    state = db.get(GamificationProfile, astronaut.id)
    assessment = latest_assessment(db, astronaut.id)
    return {
        "astronaut_id": astronaut.id,
        "name": astronaut.name or astronaut.id,
        "age": astronaut.age,
        "height_cm": astronaut.height_cm,
        "weight_kg": astronaut.weight_kg,
        "photo_url": astronaut.photo_url,
        **serialize_state(state),
        "level": (state.xp // 100 + 1) if state else 1,
        "badges": _badges(state),
        "latest_status": assessment["overall_status"] if assessment else None,
    }


def _badges(state: GamificationProfile | None) -> list[str]:
    if state is None:
        return []
    badges = []
    if state.streak >= 7:
        badges.append("7-day-streak")
    if state.points >= 100:
        badges.append("centurion")
    if state.xp >= 500:
        badges.append("space-veteran")
    return badges


@router.get("/profile/{astronaut_id}")
def get_profile(astronaut_id: str, db: Session = Depends(get_db)) -> dict:
    astronaut = db.get(Astronaut, astronaut_id)
    if astronaut is None:
        raise HTTPException(status_code=404, detail="Astronaut profile not found")
    return _profile_payload(db, astronaut)


@router.put("/profile/{astronaut_id}")
def update_profile(astronaut_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    if not astronaut_id.strip() or len(astronaut_id) > 64:
        raise HTTPException(status_code=422, detail="Invalid astronaut_id")
    unknown = set(payload) - PROFILE_FIELDS
    if unknown:
        raise HTTPException(status_code=422, detail=f"Unsupported profile fields: {', '.join(sorted(unknown))}")
    astronaut = db.get(Astronaut, astronaut_id)
    if astronaut is None:
        astronaut = Astronaut(id=astronaut_id)
        db.add(astronaut)

    for field, value in payload.items():
        if field == "name" and value is not None:
            if not isinstance(value, str) or not value.strip() or len(value.strip()) > 120:
                raise HTTPException(status_code=422, detail="name must contain 1 to 120 characters")
            value = value.strip()
        if field == "age" and value is not None and (not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 120):
            raise HTTPException(status_code=422, detail="age must be an integer from 0 to 120")
        if field in {"height_cm", "weight_kg"} and value is not None:
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or value <= 0
            ):
                raise HTTPException(status_code=422, detail=f"{field} must be a positive number")
            value = float(value)
        if field == "photo_url" and value is not None and (not isinstance(value, str) or len(value) > 500):
            raise HTTPException(status_code=422, detail="photo_url must be a string up to 500 characters")
        setattr(astronaut, field, value)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(astronaut)
    return _profile_payload(db, astronaut)


@router.get("/profiles")
def list_profiles(db: Session = Depends(get_db)) -> dict:
    astronauts = db.scalars(select(Astronaut).order_by(Astronaut.id)).all()
    return {"profiles": [_profile_payload(db, astronaut) for astronaut in astronauts]}


@router.get("/ranking")
def ranking(db: Session = Depends(get_db)) -> dict:
    return {"ranking": get_ranking(db)}
