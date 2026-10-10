from datetime import datetime

from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import SensorLog
from .schemas import (
    LatestTelemetryResponse,
    LedCommand,
    LedResponse,
    TelemetryCreate,
    TelemetryHistoryItem,
    TelemetryResponse,
)
from .services import (
    get_led_state,
    save_telemetry,
    set_led_state,
)


SIMULATOR_DEVICE_ID = "esp32-simulator-001"
REAL_DEVICE_ID = "esp32-001"

active_source = "simulator"


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API do sistema IoT ESP32.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/api/source")
def get_source():
    return {
        "source": active_source,
        "device_id": (
            SIMULATOR_DEVICE_ID
            if active_source == "simulator"
            else REAL_DEVICE_ID
        ),
    }


@app.post("/api/source")
def set_source(source: dict = Body(...)):
    global active_source

    value = source.get("source")

    if value not in {"simulator", "real"}:
        raise HTTPException(
            status_code=400,
            detail="source deve ser 'simulator' ou 'real'.",
        )

    active_source = value

    return get_source()


@app.post(
    "/api/telemetry",
    response_model=TelemetryResponse,
)
def receive_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db),
):
    expected_device_id = (
        SIMULATOR_DEVICE_ID
        if active_source == "simulator"
        else REAL_DEVICE_ID
    )

    if telemetry.device_id != expected_device_id:
        raise HTTPException(
            status_code=409,
            detail="Dispositivo não corresponde à fonte de dados ativa.",
        )

    timestamp = save_telemetry(
        db,
        telemetry,
    )

    return TelemetryResponse(
        status="ok",
        device_id=telemetry.device_id,
        timestamp=timestamp,
    )


@app.get(
    "/api/telemetry/history",
    response_model=list[TelemetryHistoryItem],
)
def telemetry_history(
    device_id: str | None = None,
    sensor_name: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=5000,
    ),
    db: Session = Depends(get_db),
):
    statement = select(SensorLog)

    if device_id:
        statement = statement.where(
            SensorLog.device_id == device_id
        )

    if sensor_name:
        statement = statement.where(
            SensorLog.sensor_name == sensor_name
        )

    if start:
        statement = statement.where(
            SensorLog.timestamp >= start
        )

    if end:
        statement = statement.where(
            SensorLog.timestamp <= end
        )

    statement = (
        statement
        .order_by(desc(SensorLog.timestamp))
        .limit(limit)
    )

    records = db.execute(
        statement
    ).scalars().all()

    return records


@app.get(
    "/api/telemetry/latest",
    response_model=LatestTelemetryResponse,
)
def latest_telemetry(
    device_id: str,
    db: Session = Depends(get_db),
):
    result = {}

    for sensor_name in (
        "temperature",
        "humidity",
        "pressure",
    ):
        statement = (
            select(SensorLog)
            .where(
                SensorLog.device_id == device_id,
                SensorLog.sensor_name == sensor_name,
            )
            .order_by(desc(SensorLog.timestamp))
            .limit(1)
        )

        record = db.execute(
            statement
        ).scalar_one_or_none()

        result[sensor_name] = (
            record.sensor_value
            if record
            else None
        )

    statement = (
        select(SensorLog)
        .where(
            SensorLog.device_id == device_id
        )
        .order_by(desc(SensorLog.timestamp))
        .limit(1)
    )

    latest = db.execute(
        statement
    ).scalar_one_or_none()

    if latest is None:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma telemetria encontrada.",
        )

    return LatestTelemetryResponse(
        device_id=device_id,
        timestamp=latest.timestamp,
        temperature=result["temperature"],
        humidity=result["humidity"],
        pressure=result["pressure"],
        button_state=latest.button_state,
    )


@app.get(
    "/api/actuators/led",
    response_model=LedResponse,
)
def get_led(
    device_id: str,
    db: Session = Depends(get_db),
):
    expected_device_id = (
        SIMULATOR_DEVICE_ID
        if active_source == "simulator"
        else REAL_DEVICE_ID
    )

    if device_id != expected_device_id:
        raise HTTPException(
            status_code=409,
            detail="Dispositivo não corresponde à fonte de dados ativa.",
        )

    actuator = get_led_state(
        db,
        device_id,
    )

    if actuator is None:
        return LedResponse(
            status="ok",
            device_id=device_id,
            led_state=False,
            updated_by="default",
            timestamp=datetime.now().astimezone(),
        )

    return LedResponse(
        status="ok",
        device_id=actuator.device_id,
        led_state=actuator.led_state,
        updated_by=actuator.updated_by,
        timestamp=actuator.timestamp,
    )


@app.post(
    "/api/actuators/led",
    response_model=LedResponse,
)
def set_led(
    command: LedCommand,
    db: Session = Depends(get_db),
):
    expected_device_id = (
        SIMULATOR_DEVICE_ID
        if active_source == "simulator"
        else REAL_DEVICE_ID
    )

    if command.device_id != expected_device_id:
        raise HTTPException(
            status_code=409,
            detail="Dispositivo não corresponde à fonte de dados ativa.",
        )

    actuator = set_led_state(
        db=db,
        device_id=command.device_id,
        led_state=command.led_state,
        updated_by=command.updated_by,
    )

    return LedResponse(
        status="ok",
        device_id=actuator.device_id,
        led_state=actuator.led_state,
        updated_by=actuator.updated_by,
        timestamp=actuator.timestamp,
    )