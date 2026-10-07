from datetime import datetime

from pydantic import BaseModel, Field


class TelemetryCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=100)

    temperature: float

    humidity: float = Field(
        ge=0,
        le=100,
    )

    pressure: float = Field(
        gt=0,
    )

    button_state: bool

    timestamp: datetime | None = None


class TelemetryResponse(BaseModel):
    status: str
    device_id: str
    timestamp: datetime


class LedCommand(BaseModel):
    device_id: str = Field(
        min_length=1,
        max_length=100,
    )

    led_state: bool

    updated_by: str = Field(
        default="api",
        max_length=100,
    )


class LedResponse(BaseModel):
    status: str
    device_id: str
    led_state: bool
    updated_by: str
    timestamp: datetime


class TelemetryHistoryItem(BaseModel):
    id: int
    timestamp: datetime
    device_id: str
    sensor_name: str
    sensor_value: float
    button_state: bool


class LatestTelemetryResponse(BaseModel):
    device_id: str
    timestamp: datetime
    temperature: float | None
    humidity: float | None
    pressure: float | None
    button_state: bool