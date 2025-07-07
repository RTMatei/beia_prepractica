import requests

from datetime import datetime, timedelta
import time

import json

# SETUP PT ARROWHEAD
orchestrator_url = "http://localhost:8441/orchestrator/orchestration"
service_definition = "humidity-temperature-sensor"

DATE_FILE = r"path\date.txt"

def get_service_url():
    payload = {
    "requesterSystem": {
        "systemName": "locallogger",
        "address": "host.docker.internal",
        "port": 8081
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

while True:
    try:
        res = requests.get(service_url)
        res.raise_for_status()
            
        sensor_data = res.json().get("data", "")
        
        if sensor_data:
            time_here = datetime.utcnow() + timedelta(hours=3) #UTC+3
            timestamp = time_here.strftime("%d/%m/%Y %H:%M:%S")
            
            parsed_data = json.loads(sensor_data)
            temperature = parsed_data.get("temperature", "N/A")
            humidity = parsed_data.get("humidity", "N/A")
            
            formatted_sensor_data = f"Temperature: {temperature}, Humidity: {humidity}"
            
            with open(DATE_FILE, "a") as f:
                f.write(f"{timestamp} - {formatted_sensor_data}" + "\n")
            print(f"[Local Log] Logged sensor data to local file.") 
            
        else:
            print("No sensor data received")
            
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(5)  # Adjust poll frequency as needed