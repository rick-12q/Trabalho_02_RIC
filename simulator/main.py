from fastapi import FastAPI
import uvicorn

from .models import LedCommand
from .sensors import update_sensor_values
from .state import DeviceState

DEVICE_ID = "esp32-simulator-001"

app = FastAPI(
    title="ESP32 Simulator",
    version="1.0.0",
)

state = DeviceState(DEVICE_ID)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "device_id": state.device_id,
    }


@app.get("/api/status")
def status():
    return {
        "device_id": state.device_id,
        "led_state": state.led_state,
        "button_state": state.button_state,
        "telemetry": state.telemetry(),
    }


@app.get("/api/telemetry")
def telemetry():
    update_sensor_values(state)
    return state.telemetry()


@app.get("/api/actuators/led")
def get_led():
    return {
        "device_id": state.device_id,
        "led_state": state.led_state,
    }


@app.post("/api/actuators/led")
def set_led(command: LedCommand):
    if command.device_id != state.device_id:
        return {
            "status": "error",
            "message": "Unknown device_id",
        }

    state.set_led(command.led_state)

    return {
        "status": "ok",
        "device_id": state.device_id,
        "led_state": state.led_state,
    }


if __name__ == "__main__":
    uvicorn.run(
        "simulator.main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
    )