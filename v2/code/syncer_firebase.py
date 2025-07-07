import time
import requests
import firebase_admin
from firebase_admin import credentials, db
import requests

from datetime import datetime, timedelta
import time

import json

# SETUP PT FIREBASE
cred = credentials.Certificate(r"path\firebasekey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://placeholder.firebasedatabase.app/'
})

# SETUP PT BACKUP
DATE_FILE = r"path\date.txt"
STATE_FILE = r"path\ultima_firebase.txt"
FIREBASE_PATH = "/data"

# SETUP PT ARROWHEAD
orchestrator_url = "http://localhost:8441/orchestrator/orchestration"
service_definition = "humidity-temperature-sensor"

def get_service_url():
    payload = {
    "requesterSystem": {
        "systemName": "firebasesyncer",
        "address": "host.docker.internal",
        "port": 8082
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

# DACA ARE CONEXIUNE LA INETERNET
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

def send_to_firebase(lines):
    ref = db.reference(FIREBASE_PATH)
    for line in lines:
        if line.strip():
            timestamp_part, data_part = line.split(" - ")
            temp_str, hum_str = data_part.split(", ")
            temperature = float(temp_str.split(": ")[1])
            humidity = float(hum_str.split(": ")[1])

            data = {
                "timestamp": timestamp_part,
                "temperature": temperature,
                "humidity": humidity
            }

            key = str(int(time.time() * 1000))
            ref.child(key).set(data)
            print(f"[Firebase] Sent: {data}")

def send_line_to_firebase(timestamp, temperature, humidity):
    ref = db.reference(FIREBASE_PATH)
    data = {
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity
    }
    key = str(int(time.time() * 1000))
    ref.child(key).set(data)
    print(f"[Firebase] Sent: {data}")

last_sent = get_last_sent_line()

while True:
    if is_online():
        unsent_lines, total_lines = read_unsent_lines(last_sent)

        if unsent_lines:
            try:
                print("######################################[RESINCRONIZARE]######################################");
                send_to_firebase(unsent_lines)
                save_last_sent_line(total_lines)
                print(f"[Firebase] S-au sincronizat {len(unsent_lines)} linii catre firebase")
                print("############################################################################################");
                last_sent = total_lines
            except Exception as e:
                print(f"[Error] Syncing backlog: {e}")
        else:
            print("[Firebase] Nu este necesara resincronizarea")
        
        try:
            res = requests.get(service_url, timeout=3)
            res.raise_for_status()
            sensor_data = res.json().get("data", "")

            if sensor_data:
                time_here = datetime.utcnow() + timedelta(hours=3)  # UTC+3
                timestamp = time_here.strftime("%d/%m/%Y %H:%M:%S")

                parsed_data = json.loads(sensor_data)
                temperature = parsed_data.get("temperature", "N/A")
                humidity = parsed_data.get("humidity", "N/A")

                send_line_to_firebase(timestamp, temperature, humidity)
                
                last_sent = last_sent + 1
                save_last_sent_line(last_sent)

            else:
                print("[Sensor] Nu s-au primit date de la senzor")

        except Exception as e:
            print(f"[Error] Reading sensor: {e}")

    else:
        print("Nu exista conexiune la internet")
        
    print("############################################################################################");

    time.sleep(5)