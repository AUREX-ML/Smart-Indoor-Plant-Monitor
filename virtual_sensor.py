import time
import json
import random
import paho.mqtt.client as mqtt

# --- CONFIGURATION ---
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "plant_monitor/sensor_01/telemetry"
CLIENT_ID = f"python-sensor-{random.randint(0, 1000)}"

# Global variable to track moisture state
current_moisture = 80.0 

# --- VIRTUAL SENSORS ---
def get_sensor_data():
    global current_moisture
    
    # 1. Simulate Natural Drying
    # Lose between 0.5% and 1.5% moisture every reading
    drying_rate = random.uniform(0.5, 1.5)
    current_moisture -= drying_rate

    # 2. Simulate "Watering" if it gets too dry (Automatic Reset)
    if current_moisture < 25.0:
        print("💧 Plant watered! Moisture resetting...")
        current_moisture = 85.0

    # 3. Add a tiny bit of random noise (sensors aren't perfect)
    sensor_noise = random.uniform(-0.5, 0.5)
    
    return {
        "moisture": round(current_moisture + sensor_noise, 2),
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(30.0, 60.0), 2),
        "timestamp": time.time()
    }

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connection Successful! ✅\n")
    else:
        print(f"❌ Failed to connect, return code {rc}")

# --- MAIN LOOP ---
# Add the CallbackAPIVersion argument as the first parameter
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID)
client.on_connect = on_connect

print("Connecting to broker ⏳ ...\n")
client.connect(BROKER, PORT)
client.loop_start()

try:
    while True:
        # 1. Generation
        payload = get_sensor_data()
        
        # 2. Transmission
        json_payload = json.dumps(payload)
        client.publish(TOPIC, json_payload)
        
        print(f"📡 Published: {json_payload}")
        
        # Wait 5 seconds before next reading
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulated Sensor Stopped.")
    client.loop_stop()
    client.disconnect()