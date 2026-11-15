from fastapi import APIRouter

from ai import local_llm
from ai.metrics_reader import get_last_reading, read_metrics

router = APIRouter(prefix="/api", tags=["AI"])


@router.post("/predict")
def predict(payload: dict):
    """Recibe las métricas de sensores del frontend y devuelve su evaluación."""
    return read_metrics(payload)


@router.post("/chat")
def chat(body: dict):
    """Conversa con la IA local (Ollama) usando la última lectura como contexto.
    Si Ollama no está disponible, responde con el resumen de métricas."""
    prompt = (body or {}).get("prompt", "").strip()
    reading = get_last_reading()

    if prompt and local_llm.is_available():
        try:
            context = reading["ai_response"] if reading else "Sin métricas registradas aún."
            reply = local_llm.chat(prompt, context)
            if reply:
                return {"reply": reply, "source": "local-llm"}
        except Exception as error:
            print(f"[chat] Ollama falló, usando respaldo: {error}")

    if reading is None:
        return {
            "reply": "Aún no tengo métricas registradas. "
                     "Ingresa datos de sensores en la pestaña DATA.",
            "source": "no-data",
        }
    return {"reply": reading["ai_response"], "source": "metrics-summary"}
