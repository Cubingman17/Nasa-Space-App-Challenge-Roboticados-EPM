from fastapi import FastAPI

app = FastAPI(
    title="Predictive AI API",
    description="Backend for our predictive AI project",
    version="0.1.0"
)


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
        port=8000
    )