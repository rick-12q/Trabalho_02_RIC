# Projeto 2 — Redes Industriais de Comunicação

<p align="center">
  <img src="https://img.shields.io/badge/UNESP-Sorocaba-1F4E79?style=for-the-badge&logo=academia&logoColor=white">
  <img src="https://img.shields.io/badge/RIC-Projeto%20Acadêmico-6C63FF?style=for-the-badge">
  <img src="https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white">
  <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Node--RED-8F0000?style=for-the-badge&logo=nodered&logoColor=white">
</p>

<p align="center">
  Sistema IoT desenvolvido para a disciplina de <strong>Redes Industriais de Comunicação — RIC</strong>,
  do curso de <strong>Engenharia de Controle e Automação</strong> da
  <strong>UNESP — Instituto de Ciência e Tecnologia de Sorocaba</strong>.
</p>

---

## Sobre o projeto

Este repositório reúne o desenvolvimento do **Projeto 2 da disciplina de Redes Industriais de Comunicação (RIC)**, cujo objetivo é integrar um sistema embarcado baseado em **ESP32** a uma arquitetura de comunicação utilizando **API REST HTTP**, banco de dados e interfaces de supervisão.

O sistema realiza a aquisição de dados de **temperatura, umidade e pressão** por meio de um sensor BME280, além da leitura de um botão físico e do controle remoto de um LED. Os dados coletados pelo ESP32 são enviados via Wi-Fi para uma API desenvolvida com **FastAPI**, responsável pela comunicação com o banco de dados **PostgreSQL** e com as diferentes interfaces do sistema.

Além do dispositivo físico, foi desenvolvido um **simulador do ESP32**, permitindo executar e testar a arquitetura sem depender permanentemente do hardware. O sistema permite alternar entre o dispositivo real e o simulado, mantendo a mesma estrutura de comunicação.

## Arquitetura do sistema

```text
                         +------------------+
                         |     Frontend     |
                         +--------+---------+
                                  |
                                  | REST HTTP
                                  v
+------------------+      +-------+--------+      +------------------+
|    ESP32 Real    | ---> |     FastAPI    | ---> |    PostgreSQL    |
| BME280 / OLED    |      |      API       |      |  Banco de dados  |
| Botão / LED      | <--- |                |      |                  |
+------------------+      +-------+--------+      +------------------+
                                  ^
                                  |
                                  |
                  +---------------+---------------+
                  |                               |
         +--------+---------+            +--------+---------+
         |    Simulador     |            |    Node-RED      |
         |      ESP32       |            |    Dashboard     |
         +------------------+            +------------------+
```

A **API REST** atua como elemento central da arquitetura, recebendo a telemetria, armazenando os dados no PostgreSQL e disponibilizando informações para o frontend e para o dashboard Node-RED.


## Tecnologias utilizadas

<p align="center">
  <img src="https://skillicons.dev/icons?i=cpp,arduino,python,fastapi,postgres,html,css,js,git,github,vscode">
</p>

O projeto utiliza **C++/Arduino** no firmware do ESP32, **Python e FastAPI** no backend e no simulador, **PostgreSQL** para persistência dos dados e **HTML, CSS e JavaScript** na interface web. O **Node-RED** é utilizado como segunda interface de supervisão e controle.

## Estrutura do repositório

```text
Trabalho_02_RIC/
│
├── Code/
│   ├── backend/          # API REST com FastAPI
│   ├── firmware/         # Firmware do ESP32 -----> CÓDIGO DO ESP ESTÁ AQUI DENTRO!
│   ├── frontend/         # Interface web
│   ├── simulator/        # Simulador do ESP32
│   └── README.md         # Instruções do ambiente
│
├── Node_red/
│   └── Node_red.json     # Fluxo completo do Node-RED
│
├── Relatorio/
│   └── ...               # Relatório e arquivos LaTeX
│
└── README.md
```

## ESP32 e hardware

O dispositivo físico é responsável pela aquisição dos dados e pela interação direta com os periféricos do sistema.

O firmware implementa:

- leitura do sensor BME280;
- leitura do botão físico;
- controle do LED;
- apresentação de informações no display OLED;
- conexão e reconexão automática ao Wi-Fi;
- envio periódico de telemetria para o backend;
- consulta do estado do LED pela API;
- servidor HTTP local;
- identificação do dispositivo na rede por mDNS;
- atualização remota do firmware utilizando OTA.

## API REST

O backend centraliza a comunicação entre os componentes da aplicação.

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Verifica o funcionamento da API |
| `GET` | `/api/source` | Consulta a fonte de dados ativa |
| `POST` | `/api/source` | Altera a fonte de dados |
| `POST` | `/api/telemetry` | Recebe dados do dispositivo |
| `GET` | `/api/telemetry/latest` | Consulta a telemetria mais recente |
| `GET` | `/api/telemetry/history` | Consulta o histórico dos sensores |
| `GET` | `/api/actuators/led` | Consulta o estado do LED |
| `POST` | `/api/actuators/led` | Altera o estado do LED |

## ESP32 real e simulador

Durante o desenvolvimento, o sistema pode operar utilizando duas fontes de dados:

| Fonte | Identificação |
|---|---|
| ESP32 real | `esp32-001` |
| Simulador | `esp32-simulator-001` |

A seleção da fonte é realizada pela própria aplicação. Dessa forma, é possível desenvolver e testar o sistema utilizando o simulador e posteriormente utilizar o ESP32 físico sem alterar a arquitetura da aplicação.

## Node-RED

O Node-RED fornece uma interface independente para supervisão e controle do sistema.

O dashboard desenvolvido permite visualizar os valores dos sensores, acompanhar o estado do botão, controlar o LED, verificar o estado das conexões e consultar informações relacionadas ao banco de dados.

O fluxo completo está disponível em:

```text
Node_red/Node_red.json
```

## OTA

O ESP32 possui suporte a **OTA (Over-the-Air)**, permitindo atualizar o firmware pela rede Wi-Fi após a programação inicial do dispositivo.

A implementação utiliza a biblioteca `ArduinoOTA`, com identificação do ESP32 por hostname e acompanhamento do processo de atualização pelo monitor serial.

## Execução

De forma geral, os serviços são inicializados na seguinte ordem:

```text
PostgreSQL
    ↓
Backend FastAPI
    ↓
Simulador
    ↓
Frontend
    ↓
Node-RED
    ↓
ESP32
```

Após a inicialização, a aplicação pode ser alternada entre **Simulador** e **ESP32 Real** por meio do seletor de fonte de dados.

## Organização acadêmica

**Universidade:** Universidade Estadual Paulista "Júlio de Mesquita Filho" — UNESP  
**Unidade:** Instituto de Ciência e Tecnologia de Sorocaba — ICTS  
**Curso:** Engenharia de Controle e Automação  
**Disciplina:** Redes Industriais de Comunicação — RIC  
**Alunos:** Luiz Henrique Corrêa Monteiro e Paulo de Melo

## Documentação

O relatório completo do projeto, incluindo metodologia, desenvolvimento, testes e resultados, está disponível no diretório:

```text
Relatorio/
```

---

<p align="center">
  <strong>UNESP — Instituto de Ciência e Tecnologia de Sorocaba</strong><br>
  Engenharia de Controle e Automação
</p>