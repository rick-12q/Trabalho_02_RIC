import asyncio
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from .models import LedCommand
from .sensors import update_sensor_values
from .state import DeviceState


DEVICE_ID = "esp32-simulator-001"

BACKEND_URL = "http://127.0.0.1:8000"

SEND_INTERVAL = 5

WEB_DIR = Path(__file__).resolve().parent / "web"


app = FastAPI(
    title="ESP32 Simulator",
    version="1.0.0",
)


state = DeviceState(
    DEVICE_ID
)


# ============================================================
# INTERFACE WEB
# ============================================================

@app.get("/")
def web_interface():

    return FileResponse(
        WEB_DIR / "index.html"
    )


@app.get("/style.css")
def web_style():

    return FileResponse(
        WEB_DIR / "style.css",
        media_type="text/css",
    )


@app.get("/script.js")
def web_script():

    return FileResponse(
        WEB_DIR / "script.js",
        media_type="application/javascript",
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "device_id": state.device_id,
    }


# ============================================================
# STATUS COMPLETO
# ============================================================

@app.get("/api/status")
def status():

    return {
        "device_id": state.device_id,
        "led_state": state.led_state,
        "button_state": state.button_state,
        "telemetry": state.telemetry(),
        "last_sent_telemetry": state.last_sent_telemetry,
        "telemetry_history": state.telemetry_history[-10:],
    }


# ============================================================
# TELEMETRIA
# ============================================================

@app.get("/api/telemetry")
def telemetry():

    update_sensor_values(
        state
    )

    return state.telemetry()


# ============================================================
# LED
# ============================================================

@app.get("/api/actuators/led")
def get_led():

    return {
        "device_id": state.device_id,
        "led_state": state.led_state,
    }


@app.post("/api/actuators/led")
def set_led(
    command: LedCommand,
):

    if command.device_id != state.device_id:

        return {
            "status": "error",
            "message": "Unknown device_id",
        }

    state.set_led(
        command.led_state
    )

    return {
        "status": "ok",
        "device_id": state.device_id,
        "led_state": state.led_state,
    }


# ============================================================
# BOTÃO FÍSICO SIMULADO
# ============================================================

@app.post("/api/button")
def set_button(
    button_state: bool,
):

    state.set_button(
        button_state
    )

    return {
        "status": "ok",
        "device_id": state.device_id,
        "button_state": state.button_state,
    }


# ============================================================
# LOOP DE TELEMETRIA
# ============================================================

async def send_telemetry_loop():

    async with httpx.AsyncClient(
        timeout=5.0
    ) as client:

        while True:

            try:

                update_sensor_values(
                    state
                )

                payload = state.telemetry()

                state.register_sent_telemetry(
                    payload
                )

                response = await client.post(
                    f"{BACKEND_URL}/api/telemetry",
                    json=payload,
                )

                if response.status_code == 200:

                    print(
                        "[SIMULATOR] Telemetria enviada:",
                        payload,
                    )

                else:

                    print(
                        "[SIMULATOR] Backend respondeu:",
                        response.status_code,
                    )

            except Exception as exc:

                print(
                    "[SIMULATOR] Backend indisponível:",
                    repr(exc),
                )

            await asyncio.sleep(
                SEND_INTERVAL
            )


# ============================================================
# POLLING DO LED
# ============================================================

async def led_polling_loop():

    async with httpx.AsyncClient(
        timeout=5.0
    ) as client:

        while True:

            try:

                response = await client.get(
                    f"{BACKEND_URL}/api/actuators/led",
                    params={
                        "device_id": DEVICE_ID,
                    },
                )

                if response.status_code == 200:

                    data = response.json()

                    new_led_state = bool(
                        data["led_state"]
                    )

                    if new_led_state != state.led_state:

                        print(
                            "[SIMULATOR] LED alterado:",
                            new_led_state,
                        )

                    state.set_led(
                        new_led_state
                    )

            except Exception as exc:

                print(
                    "[SIMULATOR] Falha consultando LED:",
                    repr(exc),
                )

            await asyncio.sleep(
                2
            )


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():

    asyncio.create_task(
        send_telemetry_loop()
    )

    asyncio.create_task(
        led_polling_loop()
    )


# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        "simulator.main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
    )