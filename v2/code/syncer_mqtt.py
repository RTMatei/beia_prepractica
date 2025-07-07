import time
import requests
import requests

import paho.mqtt.client as mqtt

import time

import json

# SETUP PT MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect("mqtt_server_address", 1883)
mqtt_client.loop_start()
topic = "mqtt_topic"

# SETUP PT BACKUP
DATE_FILE = r"path\date.txt"
STATE_FILE = r"path\ultima_mqtt.txt"

# SETUP PT ARROWHEAD
orchestrator_url = "http://localhost:8441/orchestrator/orchestration"
service_definition = "humidity-temperature-sensor"

def get_service_url():
    payload = {
    "requesterSystem": {
        "systemName": "mqttsyncer",
        "address": "host.docker.internal",
        "port": 8083
    },
    "requestedService": {
        "serviceDefinitionRequirement": "humidity-temperature-sensor"
    },
    "orchestrationFlags": {
        "overrideStore": True
    }
}

    try:
        res = requests.post(orchestrator_url, json=payload)
        res.raise_for_status()

        orchestration_response = res.json()
        print("[Orchestrator] Response received:")

        provider = orchestration_response["response"][0]["provider"]
        service_uri = orchestration_response["response"][0]["serviceUri"]  # <-- here
        
        address = provider['address']
        if address == "host.docker.internal":
            address = "127.0.0.1"

        return f"http://{address}:{provider['port']}/{service_uri.lstrip('/')}"

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        
service_url = get_service_url()
print(f"Using service URL: {service_url}")

# DACA ARE CONEXIUNE LA INTERNET
def is_online():
    try:
        requests.get("http://google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

def get_last_sent_line():
    with open(STATE_FILE, "r") as f:
        return int(f.read().strip())

def save_last_sent_line(line_num):
    with open(STATE_FILE, "w") as f:
        f.write(str(line_num))
        
def read_unsent_lines(start_line):
    with open(DATE_FILE, "r") as f:
        lines = f.readlines()
    return lines[start_line:], len(lines)

def send_to_MQTT(lines):
    for line in lines:
        if line.strip():
            timestamp_part, data_part = line.split(" - ")
            temp_str, hum_str = data_part.split(", ")
            temperature = float(temp_str.split(": ")[1])
            humidity = float(hum_str.split(": ")[1])

            data = {
                "temperature": temperature,
                "humidity": humidity
            }
            
            mqtt_client.publish(topic, json.dumps(data))
            print(f"[MQTT] Sent: {data}")

last_sent = get_last_sent_line()
last_attempt = 0
reconnect_delay = 5

while True:
    if not mqtt_client.is_connected():
        print("[MQTT] Attempting to reconnect...")
        now = time.time()
        if now - last_attempt > reconnect_delay and is_online():
            try:
                mqtt_client.reconnect()
            except Exception as e:
                print(f"[MQTT] Reconnection failed: {e}")
            last_attempt = now
    else:
        unsent_lines, total_lines = read_unsent_lines(last_sent)

        if unsent_lines:
            try:
                print("###################[RESINCRONIZARE]###################");
                send_to_MQTT(unsent_lines)
                save_last_sent_line(total_lines)
                print(f"[MQTT] S-au sincronizat {len(unsent_lines)} linii")
                print("######################################################");
                last_sent = total_lines
            except Exception as e:
                print(f"[Error] Syncing backlog: {e}")
        else:
            print("[MQTT] Nu este necesara resincronizarea")
        
        try:
            res = requests.get(service_url, timeout=3)
            res.raise_for_status()
            sensor_data = res.json().get("data", "")

            if sensor_data:
                mqtt_client.publish(topic, sensor_data)
                print(f"[MQTT] Sent: {sensor_data}")
                last_sent = last_sent + 1
                save_last_sent_line(last_sent)

            else:
                print("[Sensor] Nu s-au primit date de la senzor")

        except Exception as e:
            print(f"[Error] Reading sensor: {e}")
        
    print("######################################################");

    time.sleep(5)