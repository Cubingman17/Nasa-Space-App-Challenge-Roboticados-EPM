from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers.ai import router as ai_router
from routers.data import router as data_router

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


@app.on_event("startup")
def initialize_database():
    init_db()


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "The backend is working"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000
    )
