# Code the Future 2026

### Setup / How to run
The code inside 'src/main.cpp' is meant to be compiled and uploaded using the **Arduino IDE**, not VS Code directly. 

Make sure you install the following libraries via the Arduino Library Manager before uploading:
- 'PubSubClient'
- 'Adafruit MPU6050'

### Dashboard / Monitoring
The code inside 'dashboard/live_dashboard.py' is a Python script meant to run on the **Raspberry Pi** to monitor and process the data sent by the ESP32 via MQTT.

Make sure you install the following library on your Raspberry Pi before running:
- 'paho-mqtt'

To start the monitoring, run the following command in the terminal:
```bash
python3 dashboard/live_dashboard.py