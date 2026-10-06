from datetime import datetime

from pydantic import BaseModel, Field


class Telemetry(BaseModel):
    device_id: str = Field(min_length=1)
    temperature: float
    humidity: float = Field(ge=0, le=100)
    pressure: float = Field(gt=0)
    button_state: bool
    timestamp: datetime | None = None


class LedCommand(BaseModel):
    device_id: str = Field(min_length=1)
    led_state: bool