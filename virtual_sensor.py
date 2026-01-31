import time
import json
import random
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "plant_monitor/sensor_01/telemetry"
COMMAND_TOPIC = "plant_monitor/commands"

# Global Moisture State
current_moisture = 80.0

# --- LISTENER FUNCTION ---
def on_command(client, userdata, message):
    global current_moisture
    command = message.payload.decode("utf-8")
    
    if command == "WATER_ON":
        print("\nPUMP ACTIVATED: Watering Plant...")
        time.sleep(1) # Simulate pump running
        current_moisture = 85.0 # Reset moisture
        print("Soil is wet. Moisture reset to 85%.\n")

def on_connect(client, userdata, flags, rc):
    print(" Connected! Listening for sensor data AND commands...")
    # Subscribe to the command topic to hear the pump signal
    client.subscribe(COMMAND_TOPIC)

# Change this:
# client = mqtt.Client("python-sensor-node")

# To this:
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "python-sensor-node")
client.on_connect = on_connect
client.on_message = on_command # Attach the command listener

client.connect(BROKER, PORT)
client.loop_start() # Run background thread to listen for commands

# --- MAIN LOOP ---
try:
    while True:
        # 1. Simulate Drying (No auto-reset here anymore!)
        drying_rate = random.uniform(0.5, 1.5)
        current_moisture -= drying_rate
        
        # Cap moisture at 0 so it doesn't go negative naturally
        if current_moisture < 0: current_moisture = 0

        # 2. Publish Data
        payload = {
            "moisture": round(current_moisture, 2),
            "temperature": round(random.uniform(20, 35), 2),
            "timestamp": time.time()
        }
        client.publish(TOPIC, json.dumps(payload))
        print(f"Moisture: {payload['moisture']}%")
        
        time.sleep(2) # Faster speed for testing

except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()