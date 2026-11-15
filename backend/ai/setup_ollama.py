"""Configura el modelo personalizado AstroAI en Ollama.

Uso:  python setup_ollama.py
Hace tres cosas:
1. Verifica que el servidor de Ollama esté corriendo.
2. Descarga el modelo base (llama3.2:3b) si no existe.
3. Crea el modelo 'astroai' a partir del Modelfile de esta carpeta.
"""

import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_MODEL = "llama3.2:3b"
CUSTOM_MODEL = "astroai"
MODELFILE = Path(__file__).parent / "Modelfile"


def ollama_running() -> bool:
    try:
        with urllib.request.urlopen("http://localhost:11434/", timeout=3):
            return True
    except (urllib.error.URLError, OSError):
        return False


def run(command: list) -> bool:
    print(f"$ {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return False
    return True


def main() -> int:
    if not ollama_running():
        print("Ollama no está corriendo. Ábrelo (ollama serve o la app) y reintenta.")
        return 1

    if not run(["ollama", "pull", BASE_MODEL]):
        return 1

    if not run(["ollama", "create", CUSTOM_MODEL, "-f", str(MODELFILE)]):
        return 1

    print(f"\nModelo '{CUSTOM_MODEL}' listo. Pruébalo con:")
    print(f"  ollama run {CUSTOM_MODEL} \"me siento agotado, dormí 5 horas\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
