Content:
# ESP32 IoT System

Sistema IoT modular composto por:

- Simulador de ESP32 para desenvolvimento no PC
- Firmware ESP32 real para futura utilização com hardware
- Sensor BME280
- Backend REST API
- PostgreSQL
- Frontend web com dashboard
- Node-RED para integração e automação
- Postman para testes da API

## Estrutura

- `simulator/` — simulador do ESP32 no PC
- `firmware/` — firmware para ESP32 real
- `backend/` — API REST e regras de negócio
- `frontend/` — interface web
- `database/` — scripts SQL e configuração do banco
- `postman/` — coleções e testes da API
- `node-red/` — fluxos Node-RED
- `docs/` — documentação técnica

## Fluxo principal

ESP32/Simulador → Backend REST API → PostgreSQL

Frontend → Backend REST API

Node-RED → Backend REST API / ESP32

## Sensor

O sistema utiliza o BME280 para:

- Temperatura
- Umidade
- Pressão atmosférica

## Atuador

LED controlado remotamente através da API REST.

## Objetivo

Desenvolver primeiro todo o sistema utilizando o simulador no PC, mantendo o mesmo contrato REST que será utilizado posteriormente pelo firmware real do ESP32.