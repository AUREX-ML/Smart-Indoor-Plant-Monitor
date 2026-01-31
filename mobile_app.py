import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
COMMAND_TOPIC = "plant_monitor/commands"

def send_water_command():
    client = mqtt.Client("mobile-app-controller")
    client.connect(BROKER, PORT)
    
    print("Connecting to Mobile App 📶...")
    # Send the payload "WATER_ON"
    client.publish(COMMAND_TOPIC, "WATER_ON")
    print(f"Command sent: 'WATER_ON' to {COMMAND_TOPIC}")
    
    client.disconnect()

if __name__ == "__main__":
    confirm = input("Moisture Level Below 30%: Turn on Water Pump? (y/n): ")
    if confirm.lower() == 'y':
        send_water_command()
    else:
        print("Cancelled.")