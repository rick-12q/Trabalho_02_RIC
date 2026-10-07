# ESP32 IoT System - Architecture

## 1. Architecture

The system is divided into the following components:

- ESP32
- ESP32 Simulator
- FastAPI Backend
- PostgreSQL
- Web Frontend
- Postman
- Node-RED

Node-RED is intentionally developed separately.

## 2. Main communication

ESP32 / Simulator
        |
        | HTTP POST
        v
FastAPI Backend
        |
        | SQL
        v
PostgreSQL

Frontend
        |
        | HTTP REST
        v
FastAPI Backend

## 3. Telemetry

The ESP32 periodically sends:

- device_id
- temperature
- humidity
- pressure
- button_state
- timestamp

The backend stores each measurement in `sensor_logs`.

## 4. LED control

The Web Dashboard sends:

POST /api/actuators/led

The backend stores the desired LED state.

The ESP32 periodically requests:

GET /api/actuators/led

The ESP32 applies the returned state to GPIO2.

## 5. Simulator

The simulator reproduces the ESP32 communication flow.

It generates:

- temperature
- humidity
- pressure
- button state

and sends telemetry to the backend.

This allows development without physical hardware.

## 6. Node-RED

Node-RED will be integrated after:

1. Backend is working.
2. PostgreSQL is working.
3. Simulator is working.
4. Frontend is working.
5. ESP32 firmware is working.

The Node-RED flow will use the same REST API contract.