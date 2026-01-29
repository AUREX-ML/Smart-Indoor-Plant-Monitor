
# IoT Smart Plant Monitor (Digital Twin Simulation)

## Project Overview
The system simulates an edge device monitoring plant health, transmitting telemetry data to a central backend for processing, storage, and automated reaction.

## Architecture & Features

- **Virtual Sensor (Producer):** A Python script that mimics an ESP32 connected to DHT11 and Soil Moisture sensors. It generates synthetic environmental data and intentionally injects "sensor noise" (invalid readings) to test error handling.

- **Real-Time Communication:** Uses the MQTT protocol (via Paho-MQTT and the HiveMQ public broker) to stream JSON telemetry packets instantly.

- **Intelligent Backend (Consumer):** A listener script that ingests the stream, performs Edge Processing (filtering out noise/negative values), and archives valid data into a SQLite database for time-series analysis.

- **Automated Reaction:** Includes logic to detect critical drought conditions (Moisture < 30%). When triggered, it executes a simulated "Act" stage, printing a critical alert to the console (representing an SMS notification or water pump activation).

## Why a Digital Twin?

By building this software twin, developers can test data pipelines, refine filtering logic, and validate database schemas before deploying code to physical hardware, ensuring a more robust production environment.

**Tech Stack:** Python 3, Paho-MQTT, SQLite, JSON, Pandas.