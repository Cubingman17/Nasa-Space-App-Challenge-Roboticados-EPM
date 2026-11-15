"""Streamlit wrapper that mounts the AstroHealth AI frontend.

Runs the FastAPI backend in a background thread (port 5000) and embeds
the real HTML/JS console inside Streamlit, so a single command serves
the whole app:

    streamlit run frontend/app.py

Note: the in-app AI companion (Ollama, model "astroai") must be running
locally (see backend/ai/setup_ollama.py). On Streamlit Community Cloud the
UI renders as a visual demo; the live backend and Ollama only work when
running locally.
"""

import base64
import re
import sys
import threading
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AstroHealth AI - NASA Space Apps",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome so the console fills the screen
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
REPO_ROOT = BASE_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"

VALID_PAGES = ["index.html", "data.html", "ai.html", "profile.html"]


# -------------------------------------------------------------------------
# 1. FastAPI backend in a background thread (same process, port 5000)
# -------------------------------------------------------------------------
@st.cache_resource
def start_backend() -> str:
    """Start uvicorn once per process and return its status."""
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))

    import uvicorn
    from main import app as api_app  # backend/main.py

    server = uvicorn.Server(uvicorn.Config(
        api_app, host="127.0.0.1", port=5000, log_level="warning",
    ))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return "running"


backend_status = start_backend()


# -------------------------------------------------------------------------
# 2. HTML packager: inline logo (base64), CSS and JS into one document
# -------------------------------------------------------------------------
def get_logo_base64() -> str:
    logo_path = BASE_DIR / "Logo_NASA.webp"
    if logo_path.exists():
        encoded = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        return f"data:image/webp;base64,{encoded}"
    return ""


def render_html_page(page_filename: str) -> str:
    html_path = BASE_DIR / page_filename
    if not html_path.exists():
        return f"<h2 style='color:white;'>Error: {page_filename} not found</h2>"

    html_content = html_path.read_text(encoding="utf-8")

    # A. Embed the logo as base64 (no external file needed)
    logo_b64 = get_logo_base64()
    if logo_b64:
        html_content = re.sub(
            r'src="[^"]*Logo_NASA\.webp"', f'src="{logo_b64}"', html_content
        )

    # B. Inline local CSS files
    def inline_css(match):
        css_file = BASE_DIR / match.group(1)
        if css_file.exists():
            return f"<style>\n{css_file.read_text(encoding='utf-8')}\n</style>"
        return match.group(0)

    html_content = re.sub(
        r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>', inline_css, html_content
    )

    # C. Inline local JS files
    def inline_js(match):
        js_file = BASE_DIR / match.group(1)
        if js_file.exists():
            return f"<script>\n{js_file.read_text(encoding='utf-8')}\n</script>"
        return match.group(0)

    html_content = re.sub(
        r'<script\s+src="([^"]+\.js)"\s*></script>', inline_js, html_content
    )

    # D. Bridge script: navigate between pages via Streamlit query params
    bridge_script = """
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            document.querySelectorAll('a[href$=".html"]').forEach(link => {
                link.addEventListener("click", (e) => {
                    e.preventDefault();
                    const targetPage = link.getAttribute("href").split("?")[0];
                    const parentUrl = new URL(window.parent.location.href);
                    parentUrl.searchParams.set("page", targetPage);
                    window.parent.location.href = parentUrl.toString();
                });
            });
        });
    </script>
    """
    return html_content.replace("</body>", f"{bridge_script}\n</body>")


# -------------------------------------------------------------------------
# 3. Main render: read ?page= and embed the console
# -------------------------------------------------------------------------
active_page = st.query_params.get("page", "index.html")
if active_page not in VALID_PAGES:
    active_page = "index.html"

with st.sidebar:
    st.header("🛰️ AstroHealth AI")
    st.caption(f"Backend: **{backend_status}** on port 5000")
    chosen = st.radio("Navigate", VALID_PAGES, index=VALID_PAGES.index(active_page))
    if chosen != active_page:
        st.query_params["page"] = chosen
        st.rerun()
    st.caption("Tip: use the console sidebar or the radio above to switch screens.")

compiled_html = render_html_page(active_page)
components.html(compiled_html, height=860, scrolling=True)
