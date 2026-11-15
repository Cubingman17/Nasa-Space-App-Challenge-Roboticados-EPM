from fastapi import APIRouter, HTTPException

from ai import local_llm
from ai.metrics_reader import get_last_reading, read_metrics

router = APIRouter(prefix="/api", tags=["AI"])


@router.get("/home")
def home_data(subject: str = "A"):
    """Summary for the HOME screen based on the subject's last reading."""
    reading = get_last_reading(subject)
    if reading is None:
        return {
            "subject": subject,
            "ai_advice": "No metrics registered yet. Log your data in the DATA tab.",
            "missions": 0,
        }
    return {
        "subject": subject,
        "ai_advice": reading["ai_response"],
        "missions": 1,
    }


@router.post("/predict")
def predict(payload: dict):
    """Receives the frontend sensor metrics and returns their evaluation."""
    try:
        return read_metrics(payload)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/chat")
def chat(body: dict):
    """Chats with the local AI (Ollama) using the subject's last reading
    as context. If Ollama is not available, replies with the metrics
    summary."""
    body = body or {}
    prompt = (body.get("prompt") or "").strip()
    subject = body.get("subject_id") or "A"
    reading = get_last_reading(subject)

    if prompt and local_llm.is_available():
        try:
            context = reading["ai_response"] if reading else "No metrics registered yet."
            reply = local_llm.chat(prompt, context)
            if reply:
                return {"reply": reply, "source": "local-llm"}
        except Exception as error:
            print(f"[chat] Ollama failed, using fallback: {error}")

    if reading is None:
        return {
            "reply": "No metrics registered yet. "
                     "Enter sensor data in the DATA tab.",
            "source": "no-data",
        }
    return {"reply": reading["ai_response"], "source": "metrics-summary"}
