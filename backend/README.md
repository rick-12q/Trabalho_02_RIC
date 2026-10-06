Content:
# Backend

Backend REST API do sistema IoT.

Responsabilidades futuras:

- Receber telemetria do ESP32/simulador
- Armazenar dados no PostgreSQL
- Consultar histórico de telemetria
- Consultar estado do dispositivo
- Controlar o LED
- Validar requisições
- Fornecer respostas JSON
- Registrar erros e eventos relevantes

O backend deverá utilizar variáveis de ambiente para configurações e credenciais.

A API deverá manter um contrato estável para que o simulador, o firmware real, o frontend, o Node-RED e o Postman possam utilizá-la.