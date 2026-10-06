Content:
# Architecture

## Main components

- ESP32 Simulator
- ESP32 Firmware
- Backend REST API
- PostgreSQL
- Frontend Dashboard
- Node-RED
- Postman

## Main data flow

ESP32 Simulator / ESP32
        |
        v
Backend REST API
        |
        v
PostgreSQL

Frontend Dashboard
        |
        v
Backend REST API

Node-RED
        |
        +---- Backend REST API
        |
        +---- ESP32 / Simulator

## Development strategy

The simulator will be implemented first so that the complete software system can be developed and tested without physical ESP32 hardware.

The real ESP32 firmware must follow the same communication contract as the simulator.

Node-RED will be developed separately after the main software system is functional.

The system should remain modular so that replacing the simulator with the real ESP32 does not require changes to the backend or frontend.