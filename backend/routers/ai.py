from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from database import get_db
    from services.ai_service import analyze, chat as chat_service
except ModuleNotFoundError:
    from backend.database import get_db
    from backend.services.ai_service import analyze, chat as chat_service

router = APIRouter(prefix="/api", tags=["AI"])


@router.post("/predict")
def predict(payload: dict, db: Session = Depends(get_db)):
    """Evaluate and save the frontend sensor metrics."""
    try:
        return analyze(payload or {}, db)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/chat")
def chat(body: dict, db: Session = Depends(get_db)):
    """Chat using the astronaut's latest persisted health assessment."""
    body = body or {}
    prompt = (body.get("prompt") or "").strip()
    subject = body.get("subject_id") or "A"
    try:
        return chat_service(prompt, subject, db)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
