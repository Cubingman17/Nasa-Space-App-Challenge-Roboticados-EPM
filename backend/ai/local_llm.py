"""Conversación con la IA local AstroAI (modelo custom de Ollama).

La personalidad del asistente (salud física + apoyo emocional) vive en el
Modelfile de esta carpeta; se crea con:  python setup_ollama.py

Usa solo la librería estándar para no agregar dependencias.
Si Ollama no está corriendo o falla, el router cae a un mensaje de respaldo.
"""

import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "astroai"
TIMEOUT_SECONDS = 90


def is_available() -> bool:
    """True si el servidor de Ollama responde."""
    try:
        with urllib.request.urlopen("http://localhost:11434/", timeout=3):
            return True
    except (urllib.error.URLError, OSError):
        return False


def chat(prompt: str, metrics_context: str = "") -> str:
    """Envía el mensaje del astronauta a la IA local junto con el contexto
    de sus métricas. Devuelve el texto de respuesta."""
    user_content = prompt
    if metrics_context:
        user_content = (
            f"Métricas actuales del astronauta:\n{metrics_context}\n\n"
            f"Mensaje del astronauta: {prompt}"
        )

    payload = json.dumps({
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "user", "content": user_content},
        ],
        "options": {"temperature": 0.6},
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("message", {}).get("content", "").strip()
