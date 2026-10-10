# ESP32 IoT System

Complete IoT system based on ESP32, REST API, PostgreSQL and Web Dashboard.

## Components

- ESP32
- BME280/DHT sensor
- Physical button
- Internal ESP32 LED
- Wi-Fi
- OTA
- FastAPI
- PostgreSQL
- Web Dashboard
- Postman
- ESP32 Simulator
- Node-RED

## Architecture

ESP32 / Simulator
        |
        v
FastAPI
        |
        v
PostgreSQL

Frontend
        |
        v
FastAPI

Node-RED
        |
        v
FastAPI / ESP32

## Development order

1. PostgreSQL
2. Backend
3. Simulator
4. Postman
5. Frontend
6. ESP32
7. OTA
8. Node-RED

## Backend

Run:

python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

## Simulator

Run:

python -m simulator.main

## Frontend

Open:

frontend/index.html

or use VS Code Live Server.

## API

GET /health

POST /api/telemetry

GET /api/telemetry/latest

GET /api/telemetry/history

GET /api/actuators/led

POST /api/actuators/led

## Node-RED

Node-RED is intentionally excluded from the first implementation stage.

It will be developed after the complete base system has been validated.