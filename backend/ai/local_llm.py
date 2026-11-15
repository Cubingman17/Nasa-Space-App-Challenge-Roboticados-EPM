"""Chat with the local AstroAI (custom Ollama model).

The assistant persona (physical health + emotional support) lives in the
Modelfile in this folder; it is created with:  python setup_ollama.py

Uses only the standard library to avoid extra dependencies.
If Ollama is not running or fails, the router falls back to a canned reply.
"""

import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "astroai"
TIMEOUT_SECONDS = 90


def is_available() -> bool:
    """True if the Ollama server responds."""
    try:
        with urllib.request.urlopen("http://localhost:11434/", timeout=3):
            return True
    except (urllib.error.URLError, OSError):
        return False


def chat(prompt: str, metrics_context: str = "") -> str:
    """Sends the astronaut's message to the local AI together with the
    context of their metrics. Returns the response text."""
    user_content = prompt
    if metrics_context:
        user_content = (
            f"Current astronaut metrics:\n{metrics_context}\n\n"
            f"Astronaut message: {prompt}"
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
