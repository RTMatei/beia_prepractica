import serial
import paho.mqtt.client as mqtt

from web3 import Web3
from datetime import datetime

#SETUP PT MQTT
ser = serial.Serial('COM3', 9600, timeout=1)
mqtt_client = mqtt.Client()
mqtt_client.connect("mqtt_server_address", 1883)
topic = "mqtt_topic"

#SETUP PT BLOCKCHAIN (cu GANACHE)
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
sender = web3.eth.accounts[0]
receiver = web3.eth.accounts[1]

while True:
    line = ser.readline().decode('utf-8').strip()
    if line:
        print(f"Publishing: {line}")
        mqtt_client.publish(topic, line)
        
        timestamp = datetime.utcnow().isoformat()
        try:
            tx = web3.eth.send_transaction({
                'from': sender,
                'to': receiver,
                'value': 0,
                'data': web3.to_bytes(text=f"{timestamp} - {line}")
            })
            print(f"[Blockchain] Tx sent: {tx.hex()}")
        except Exception as e:
            print(f"[Blockchain] Error: {e}")