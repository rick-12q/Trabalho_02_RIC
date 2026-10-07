# Installation Guide

# 1. Requirements

Install:

- Python 3.11+
- PostgreSQL
- Arduino IDE
- ESP32 Arduino Core
- Postman

Node-RED is not required during the first stage.

# 2. PostgreSQL

Create a database called:

esp32_iot

Example:

CREATE DATABASE esp32_iot;

Then execute:

database/01_schema.sql

# 3. Python environment

Open PowerShell in the project root.

Create virtual environment:

python -m venv .venv

Activate:

.\.venv\Scripts\Activate.ps1

Install backend dependencies:

pip install -r backend/requirements.txt

Install simulator dependencies:

pip install -r simulator/requirements.txt

# 4. Environment

Create:

.env

Example:

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/esp32_iot
CORS_ORIGINS=*

Adjust username/password if necessary.

# 5. Start backend

From the project root:

python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

Test:

GET http://127.0.0.1:8000/health

# 6. Start simulator

Open another terminal.

Activate the virtual environment.

Run:

python -m simulator.main

Simulator address:

http://127.0.0.1:8001

The simulator will periodically send telemetry to the backend.

# 7. Test API

Open Postman.

Import:

postman/ESP32_IoT.postman_collection.json

Run:

Health

Then:

Enviar Telemetria

Then:

Última Telemetria

Then:

Histórico Temperatura

Then:

Ligar LED

Then:

Desligar LED

# 8. Frontend

Open:

frontend/index.html

For development, preferably use the VS Code Live Server extension.

The frontend connects to:

http://127.0.0.1:8000

# 9. ESP32

Open:

firmware/esp32/esp32_iot.ino

Change:

WIFI_SSID

WIFI_PASSWORD

BACKEND_HOST

BACKEND_HOST must be the LAN IP of the computer running FastAPI.

Do NOT use:

127.0.0.1

because 127.0.0.1 on the ESP32 refers to the ESP32 itself.

Upload the firmware using USB first.

After the first successful connection, OTA can be used for future uploads.

# 10. Test sequence

Recommended order:

1. PostgreSQL
2. FastAPI
3. Simulator
4. Postman
5. Frontend
6. ESP32
7. OTA
8. Node-RED

Node-RED should only be added after the base system is validated.