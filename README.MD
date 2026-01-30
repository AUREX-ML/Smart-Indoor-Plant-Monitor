
# IoT Smart Indoor Plant Monitor (With AI Prediction)

## 📖 Project Overview
This system is a comprehensive **Digital Twin simulation** of an IoT Smart Plant Monitor. It mimics the full data lifecycle—from Edge generation to Cloud processing—without requiring physical hardware.

Unlike standard monitors that only alert you when a plant is *already* dry, this system uses **Machine Learning (Linear Regression)** to analyze soil moisture trends in real-time and **predict** exactly when the plant will need water, allowing for proactive care.

## 🏗 Architecture & Features

### 1. The Virtual Sensor (Producer / Edge)
*   **Realistic Simulation:** Replaces the ESP32 hardware with a Python script.
*   **Natural Drying Cycle:** Instead of random numbers, the sensor mimics a realistic "drying curve" (moisture decreasing over time).
*   **Simulated Noise:** Intentionally injects occasional "sensor noise" (negative values or voltage spikes) and "automatic watering" events to test the backend's error handling and logic.

### 2. Communication & Ingestion
*   **Protocol:** Uses **MQTT** (Message Queuing Telemetry Transport) via `paho-mqtt` for lightweight, real-time data transmission.
*   **Broker:** Connects to the public **HiveMQ** broker, simulating a real cloud connection.

### 3. Intelligent Backend (Consumer / Cloud)
*   **Data Cleaning:** Filters out corrupt data packets (sensor noise) before processing.
*   **Storage:** Logs valid telemetry data into a local **SQLite** database for historical persistence.
*   **Data Portability:** Automatically exports the full dataset to a **CSV file** upon system exit, ready for analysis in Excel or Google Sheets.

### 4. AI Analysis & Prediction Engine
*   **Trend Analysis:** Uses **Scikit-Learn** to perform Linear Regression on the incoming data stream.
*   **Predictive Alerts:** Calculates the rate of soil drying and forecasts the specific time the moisture will drop below the critical threshold (30%).
    *   *Old Way:* "Alert: Moisture is low!" (Reactive)
    *   *New Way:* "AI Forecast: Water needed today at 4:30 PM." (Proactive)

### 5. Automated Reaction (The "Act" Stage)
*   **Triggers:** Monitors for critical drought conditions (< 30%).
*   **Action:** Executes a simulated actuator response (e.g., printing "PUMP ACTIVATED" logs) if the AI prediction is ignored and the plant reaches critical levels.

---

## 🛠 Tech Stack
*   **Language:** Python 3.9
*   **IoT Protocol:** Paho-MQTT
*   **Database:** SQLite3
*   **Data Science:** Pandas (Data manipulation), Scikit-Learn (Linear Regression), NumPy
*   **Format:** JSON Telemetry

---

## 🚀 How to Run

1.  **Install Dependencies:**
    ```bash
    pip install paho-mqtt pandas scikit-learn
    ```

2.  **Start the Backend (The Brain):**
    Open a terminal and run the monitor. It will initialize the database and wait for data.
    ```bash
    python backend_monitor.py
    ```

3.  **Start the Sensor (The Source):**
    Open a second terminal and run the sensor simulation.
    ```bash
    python virtual_sensor.py
    ```

4.  **Observe:**
    *   Watch the backend clean incoming data.
    *   Wait ~1 minute for enough data points to accumulate.
    *   View the **AI Forecast** predictions appearing in the console.

5.  **Finish:**
    Press `Ctrl+C` on the backend terminal to stop the system and automatically generate the **CSV Data Dump**.

---

## 💡 Why a Digital Twin?
By building this software twin, we can validate the entire data pipeline, refine the **Machine Learning model**, and test database schemas before spending money on physical sensors. It ensures that when we do switch to hardware (ESP32 + Capacitive Soil Sensor), the logic is already proven to work.