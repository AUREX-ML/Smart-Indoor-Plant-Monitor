import json
import csv
import sqlite3
import numpy as np
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion 
from datetime import datetime, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression

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

def export_to_csv():
    """
    Reads the entire SQLite database and exports it to a CSV file
    for use in Excel/Google Sheets.
    """
    try:
        print("💾 Exporting database to CSV...")
        conn = sqlite3.connect(DB_NAME)
        
        # Use Pandas to grab the whole table in one line
        df = pd.read_sql_query("SELECT * FROM sensor_logs", conn)
        conn.close()
        
        if not df.empty:
            # Create a filename with the current timestamp so you don't overwrite old ones
            filename = f"plant_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Success! Data saved to: {filename}")
        else:
            print("⚠️ Database is empty. No CSV created.")

    except Exception as e:
        print(f"❌ Export Failed: {e}")

# --- MODEL SETUP ---
def run_ai_prediction():
    """Runs Linear Regression on the last 50 records"""
    try:
        conn = sqlite3.connect(DB_NAME)
        # Get the last 50 readings for the most recent trend
        df = pd.read_sql_query("SELECT timestamp, moisture FROM sensor_logs ORDER BY id DESC LIMIT 50", conn)
        conn.close()

        if len(df) < 10: return # Not enough data yet

        # Prepare Data
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # We need to flip it so the oldest of the 50 is at the top for the math to work
        df = df.iloc[::-1].reset_index(drop=True) 
        
        # Convert time to "seconds from now"
        now = datetime.now()
        df['seconds_offset'] = (df['timestamp'] - now).dt.total_seconds()

        X = df[['seconds_offset']].values
        y = df['moisture'].values

        # Train Model
        model = LinearRegression()
        model.fit(X, y)
        slope = model.coef_[0]
        intercept = model.intercept_ # This is roughly the moisture "right now"

        # Predict time until 30%
        # 30 = slope * X + intercept  =>  X = (30 - intercept) / slope
        if slope < 0: # Only predict if drying
            seconds_until_critical = (30.0 - intercept) / slope
            if seconds_until_critical > 0:
                predicted_time = now + timedelta(seconds=seconds_until_critical)
                print(f"🔮 AI FORECAST: Water needed at {predicted_time.strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"AI Error: {e}")


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
message_counter = 0
def process_data(client, userdata, message):
    global message_counter
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

        # 3. AI Step (Run every 5 messages to save CPU)
        message_counter += 1
        if message_counter % 5 == 0:
            print("🧠 Running Health Analysis...")
            run_ai_prediction()

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

# --- MAIN LOOP ---
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nBackend Stopped.")

    export_to_csv()

    client.disconnect()