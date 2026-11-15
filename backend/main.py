from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

try:
    from backend.database import init_db
    from backend.routers.ai import router as ai_router
    from backend.routers.data import router as data_router
    from backend.routers.home import router as home_router
    from backend.routers.profile import router as profile_router
except ModuleNotFoundError:
    from database import init_db
    from routers.ai import router as ai_router
    from routers.data import router as data_router
    from routers.home import router as home_router
    from routers.profile import router as profile_router

REPO_ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="Astronaut Health API",
    description="API for astronaut health metrics and data availability.",
    version="0.1.0"
)

# The frontend is static (file:// or another port), so it needs CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)
app.include_router(data_router)
app.include_router(home_router)
app.include_router(profile_router)


@app.on_event("startup")
def initialize_database():
    init_db()


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }


# Serve the whole web console (index.html + frontend assets) from the
# repo root, so one local URL hosts both the UI and the API.
app.mount("/", StaticFiles(directory=REPO_ROOT, html=True), name="console")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000
    )
