import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import re
import json

# Configuración de página completa en Streamlit
st.set_page_config(
    page_title="AstroHealth AI - NASA Space Apps",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar márgenes y menús superiores de Streamlit para que la tablet web ocupe toda la pantalla
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }
        iframe {
            border: none !important;
            border-radius: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).parent

# -------------------------------------------------------------------------
# 1. LÓGICA DE BACKEND EN PYTHON (Aqui conectarás tu modelo entrenado)
# -------------------------------------------------------------------------
def evaluar_estado_astronauta(lpm: float, sueno: float, reaccion_ms: float) -> dict:
    """
    Calcula el estado cromático (green, yellow, red) y los riesgos
    que se inyectarán directamente en el frontend HTML/JS.
    """
    if reaccion_ms > 500 or sueno < 5.5 or lpm > 100:
        return {
            "overall_status": "red",
            "status_label": "ALERTA CRÍTICA (Z > 2.5)",
            "level": 4,
            "xp_percent": 50,
            "ai_advice": f"Alerta en Python: Reacción ({reaccion_ms}ms) o sueño ({sueno}h) fuera de rango óptimo. Descanso recomendado.",
            "risks": {
                "radiation": {"level": "ALTO", "color": "red"},
                "gravity": {"level": "MODERADO", "color": "yellow"},
                "psicology": {"level": "ALTO", "color": "red"},
                "environment": {"level": "ÓPTIMO", "color": "green"}
            }
        }
    elif reaccion_ms > 350 or sueno < 6.5 or lpm > 85:
        return {
            "overall_status": "yellow",
            "status_label": "PRECAUCIÓN (Z 1.5 - 2.5)",
            "level": 4,
            "xp_percent": 70,
            "ai_advice": f"Precaución: Ligera fatiga detectada ({sueno}h de sueño). Prioriza recuperación.",
            "risks": {
                "radiation": {"level": "ALTO", "color": "red"},
                "gravity": {"level": "MODERADO", "color": "yellow"},
                "psicology": {"level": "MODERADO", "color": "yellow"},
                "environment": {"level": "ÓPTIMO", "color": "green"}
            }
        }
    else:
        return {
            "overall_status": "green",
            "status_label": "ÓPTIMO (Z < 1.5)",
            "level": 5,
            "xp_percent": 88,
            "ai_advice": f"Parámetros nominales en Python: Sueño ({sueno}h) y reacción ({reaccion_ms}ms) en rango óptimo.",
            "risks": {
                "radiation": {"level": "ALTO", "color": "red"},
                "gravity": {"level": "MODERADO", "color": "yellow"},
                "psicology": {"level": "BAJO", "color": "green"},
                "environment": {"level": "ÓPTIMO", "color": "green"}
            }
        }

# -------------------------------------------------------------------------
# 2. EMPAQUETADOR DE HTML + CSS + JS + IMÁGENES PARA STREAMLIT
# -------------------------------------------------------------------------
def get_logo_base64() -> str:
    logo_path = BASE_DIR / "Logo_NASA.webp"
    if logo_path.exists():
        b64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        return f"data:image/webp;base64,{b64}"
    return ""

def render_html_page(page_filename: str, python_state: dict) -> str:
    html_path = BASE_DIR / page_filename
    if not html_path.exists():
        return f"<h2 style='color:white;'>Error: No se encontró {page_filename}</h2>"

    html_content = html_path.read_text(encoding="utf-8")

    # A. Reemplazar ruta local absoluta del logo por Base64 embebido
    logo_b64 = get_logo_base64()
    if logo_b64:
        html_content = re.sub(r'src="[^"]*Logo_NASA\.webp"', f'src="{logo_b64}"', html_content)

    # B. Inyectar archivos CSS locales dentro de <style>
    def inline_css(match):
        css_rel = match.group(1)
        css_file = BASE_DIR / css_rel
        if css_file.exists():
            return f"<style>\n{css_file.read_text(encoding='utf-8')}\n</style>"
        return match.group(0)

    html_content = re.sub(r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>', inline_css, html_content)

    # C. Inyectar archivos JS locales dentro de <script>
    def inline_js(match):
        js_rel = match.group(1)
        js_file = BASE_DIR / js_rel
        if js_file.exists():
            return f"<script>\n{js_file.read_text(encoding='utf-8')}\n</script>"
        return match.group(0)

    html_content = re.sub(r'<script\s+src="([^"]+\.js)"\s*></script>', inline_js, html_content)

    # D. Script puente para navegación dentro de Streamlit y sincronización de estado Python
    bridge_script = f"""
    <script>
        // Guardar estado calculado por Python en localStorage y aplicar colores
        const INITIAL_PYTHON_STATE = {json.dumps(python_state)};
        if (!localStorage.getItem("astroState")) {{
            localStorage.setItem("astroState", JSON.stringify(INITIAL_PYTHON_STATE));
        }}

        document.addEventListener("DOMContentLoaded", () => {{
            if (typeof applyPythonStateToUI === "function") {{
                const current = JSON.parse(localStorage.getItem("astroState")) || INITIAL_PYTHON_STATE;
                applyPythonStateToUI(current);
            }}

            // Interceptar enlaces de navegación (index.html, data.html, ai.html, profile.html)
            // para cambiar de página mediante query params de Streamlit
            document.querySelectorAll('a[href$=".html"]').forEach(link => {{
                link.addEventListener("click", (e) => {{
                    e.preventDefault();
                    const targetPage = link.getAttribute("href").split("?")[0];
                    const parentUrl = new URL(window.parent.location.href);
                    parentUrl.searchParams.set("page", targetPage);
                    window.parent.location.href = parentUrl.toString();
                }});
            }});
        }});
    </script>
    """
    html_content = html_content.replace("</body>", f"{bridge_script}\n</body>")
    return html_content

# -------------------------------------------------------------------------
# 3. EJECUCIÓN PRINCIPAL DE STREAMLIT
# -------------------------------------------------------------------------
# Leer página activa desde la URL (?page=index.html, data.html, ai.html, profile.html)
query_params = st.query_params
active_page = query_params.get("page", "index.html")

valid_pages = ["index.html", "data.html", "ai.html", "profile.html"]
if active_page not in valid_pages:
    active_page = "index.html"

# Panel opcional lateral colapsado por si quieres simular datos directo desde Python
with st.sidebar:
    st.header("🐍 Simulador Backend Python")
    st.caption("Ajusta valores para enviar nuevo estado a la UI:")
    sim_lpm = st.slider("Pulso (LPM)", 50, 140, 68)
    sim_sueno = st.slider("Horas de Sueño", 3.0, 10.0, 7.5, 0.5)
    sim_rt = st.slider("Reacción PVT (ms)", 180, 700, 240)
    if st.button("Enviar Estado desde Python"):
        st.session_state["py_state"] = evaluar_estado_astronauta(sim_lpm, sim_sueno, sim_rt)
        st.rerun()

# Obtener estado actual de Python
current_python_state = st.session_state.get(
    "py_state",
    evaluar_estado_astronauta(lpm=68, sueno=7.5, reaccion_ms=240)
)

# Renderizar la web completa dentro de Streamlit
compiled_html = render_html_page(active_page, current_python_state)
components.html(compiled_html, height=760, scrolling=True)