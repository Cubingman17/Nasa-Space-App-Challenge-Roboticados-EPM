from fastapi import FastAPI

app = FastAPI(
    title="Astronaut Health API",
    description="API for astronaut health metrics and data availability.",
    version="0.1.0",
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
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000
    )
