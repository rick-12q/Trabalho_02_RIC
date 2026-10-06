from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="ESP32 Simulator",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "device_id": "esp32-simulator-001",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
    )