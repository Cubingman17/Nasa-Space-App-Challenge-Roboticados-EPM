from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from database import get_db
    from models.schemas import ChatRequest
    from services.ai_service import analyze, chat as chat_service
except ModuleNotFoundError:
    from backend.database import get_db
    from backend.models.schemas import ChatRequest
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
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    """Chat using the astronaut's latest persisted health assessment."""
    try:
        return chat_service(body.prompt, body.subject_id, db)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
