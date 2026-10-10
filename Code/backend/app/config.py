from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ESP32 IoT Backend"
    app_version: str = "1.0.0"

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/esp32_iot"
    )

    cors_origins: str = "*"

    telemetry_default_limit: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()