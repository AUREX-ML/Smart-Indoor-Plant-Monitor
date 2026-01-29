import time
import json
import random
import paho.mqtt.client as mqtt

# --- CONFIGURATION ---
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "plant_monitor/sensor_01/telemetry"
CLIENT_ID = f"python-sensor-{random.randint(0, 1000)}"

def get_sensor_data():
    """
    Simulates reading from DHT11 and Soil Moisture sensors.
    Includes logic to introduce artificial 'noise' for the backend to filter.
    """
    # Simulate valid ranges
    moisture = round(random.uniform(10.0, 80.0), 2)
    temp = round(random.uniform(20.0, 35.0), 2)
    humidity = round(random.uniform(30.0, 60.0), 2)

    # Simulate 'Sensor Noise' (e.g., loose wire causing negative values)
    # 10% chance to send garbage data
    if random.random() < 0.1:
        moisture = -50.0 

    return {
        "moisture": moisture,
        "temperature": temp,
        "humidity": humidity,
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