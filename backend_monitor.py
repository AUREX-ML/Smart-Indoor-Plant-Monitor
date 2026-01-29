import json
import sqlite3
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion 
from datetime import datetime

# --- CONFIGURATION ---
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "plant_monitor/sensor_01/telemetry"
DB_NAME = "plant_data.db"

# --- DATABASE SETUP ---
def init_db():
    """Creates the local database table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            moisture REAL,
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("📂 Database initialized.")

def save_to_db(data):
    """Logs clean data to SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_logs (timestamp, moisture, temperature, humidity)
        VALUES (?, ?, ?, ?)
    ''', (datetime.fromtimestamp(data['timestamp']), data['moisture'], data['temperature'], data['humidity']))
    conn.commit()
    conn.close()
    print("💾 Data saved to Storage.")

# --- ACTION LAYER ---
def trigger_alert(moisture):
    """
    Simulates the Twilio SMS / Water Pump activation.
    """
    print("\n🚨 CRITICAL ALERT 🚨")
    print(f"   Moisture Level: {moisture}% (BELOW 30%)")
    print("   -> 📲 SMS Sent: 'Water your plant!'")
    print("   -> 💧 Water Pump ACTIVATED")
    print("-" * 30 + "\n")

# --- PROCESSING LAYER ---
def process_data(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        data = json.loads(payload)
        
        print(f"📥 Received raw data: {data}")

        # 1. Cleaning Step (Filter out sensor noise)
        if data['moisture'] < 0:
            print("⚠️ Invalid reading detected (Sensor Noise). Discarding.")
            return

        # 2. Storage Step
        save_to_db(data)

        # 3. Reaction Step
        if data['moisture'] < 30.0:
            trigger_alert(data['moisture'])

    except Exception as e:
        print(f"Error processing message: {e}")

# --- MQTT SETUP ---
# Tell the library to use the Version 2 rules
client = mqtt.Client(CallbackAPIVersion.VERSION2, "python-backend-listener")
client.on_message = process_data

print("Starting Backend System...")
init_db()

client.connect(BROKER, PORT)
client.subscribe(TOPIC)
print(f"👂 Listening on topic: {TOPIC}")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nBackend Stopped.")