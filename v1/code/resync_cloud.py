import time
import os
import requests
import firebase_admin
from firebase_admin import credentials, db

# setup pt firebase
cred = credentials.Certificate(r"path\firebasekey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://placeholder.firebasedatabase.app/'
})

# setup pt backup
DATE_FILE = r"path.date.txt"
STATE_FILE = r"path.ultima.txt"
FIREBASE_PATH = "/data"

# daca e conectat la net
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

while True:
    last_sent = get_last_sent_line()
    if is_online():
        unsent_lines, total_lines = read_unsent_lines(last_sent)
        if unsent_lines:
            send_to_firebase(unsent_lines)
            save_last_sent_line(total_lines)
            print(f"S-au sincronizat {len(unsent_lines)} linii")
        else:
            print("Nu este necesara resincronizarea")
    else:
        print("Nu exista conexiune la internet")
    time.sleep(2)

