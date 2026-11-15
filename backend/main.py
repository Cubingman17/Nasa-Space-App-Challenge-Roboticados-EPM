from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.ai import router as ai_router

app = FastAPI(
    title="Predictive AI API",
    description="Backend for our predictive AI project",
    version="0.1.0"
)

# El frontend es estático (file:// u otro puerto), por eso necesita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "The backend is working"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "model_trained": False
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000
    )
