from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import requests

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

DATE_FILE = r"path\date.txt"

def load_date_txt_summary():
    if not os.path.exists(DATE_FILE):
        return None

    temps = []
    humidities = []
    timestamps = []

    line_pattern = re.compile(
        r"^(?P<timestamp>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - Temperature: (?P<temp>[\d.]+), Humidity: (?P<hum>[\d.]+)"
    )

    with open(DATE_FILE, "r") as file:
        for line in file:
            match = line_pattern.match(line.strip())
            if match:
                timestamps.append(match.group("timestamp"))
                temps.append(float(match.group("temp")))
                humidities.append(float(match.group("hum")))

    if not temps:
        return None

    return {
        "temperatures": temps,
        "humidities": humidities,
        "timestamps": timestamps
    }

def build_system_prompt(data):
    temps = data["temperatures"]
    hums = data["humidities"]
    times = data["timestamps"]

    summary = (
        f"The file contains {len(temps)} measurements.\n"
        f"The first recorded temperature is {temps[0]} °C and humidity {hums[0]}%.\n"
        f"The last recorded temperature is {temps[-1]} °C and humidity {hums[-1]}%.\n"
        f"The minimum temperature is {min(temps)} °C.\n"
        f"The maximum temperature is {max(temps)} °C.\n"
        f"The average temperature is {round(sum(temps)/len(temps), 2)} °C.\n"
        f"The minimum humidity is {min(hums)}%.\n"
        f"The maximum humidity is {max(hums)}%.\n"
        f"The average humidity is {round(sum(hums)/len(hums), 2)}%.\n"
        f"The first timestamp is {times[0]}, the last is {times[-1]}.\n"
    )

    return (
        "You are a laid back assistant analyzing a dataset of temperature and humidity measurements.\n\n"
        "Here is a summary of the dataset:\n"
        f"{summary}\n"
        "You can now answer questions about the dataset based on this summary.\n"
        "Respond in Markdown.\n"
    )

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("question")
    data = load_date_txt_summary()
    if not data:
        return jsonify({"response": "The date.txt file is missing or contains no valid data."})

    system_prompt = build_system_prompt(data)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "stream": False
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=30)
        response.raise_for_status()
        answer = response.json()["message"]["content"]
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"response": f"Error: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)