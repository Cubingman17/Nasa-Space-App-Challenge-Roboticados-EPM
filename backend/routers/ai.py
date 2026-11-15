from fastapi import APIRouter

from ai import local_llm
from ai.metrics_reader import get_last_reading, read_metrics

router = APIRouter(prefix="/api", tags=["AI"])


@router.post("/predict")
def predict(payload: dict):
    """Receives the frontend sensor metrics and returns their evaluation."""
    return read_metrics(payload)


@router.post("/chat")
def chat(body: dict):
    """Chats with the local AI (Ollama) using the last reading as context.
    If Ollama is not available, replies with the metrics summary."""
    prompt = (body or {}).get("prompt", "").strip()
    reading = get_last_reading()

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
