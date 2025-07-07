from flask import Flask, jsonify
import serial
import threading

app = Flask(__name__)
ser = serial.Serial('COM3', 9600, timeout=1)

latest_data = None  # global variable to store the latest sensor value

def read_serial():
    global latest_data
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            latest_data = line

# Start background thread to read serial continuously
threading.Thread(target=read_serial, daemon=True).start()

@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    if latest_data:
        return jsonify({"data": latest_data})
    else:
        return jsonify({"data": "No data yet"}), 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
