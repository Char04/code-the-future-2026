# Code the Future 2026

# Comunicare Drona-Turn de Control - VirtualBB Hackathon Siemens 2026

A project that simulates the communication between a drone and a control tower/station. In this project we're using an ESP32 to simulate the internal computer of a drone that connects and sends real-time data to a Raspberry Pi which acts as the control tower.

## Main Features
* A visual interface built in Python (Tkinter) on a Raspberry Pi that displays in real-time the data that are transmitted from the ESP32 board.
* A settings module that allows applying offsets to received sensor values in order to test the drone's safety warnings. You can change the following:
  * Altitude - altering reference value and warning threshold
  * Atmospheric Pressure - altering reference threshold
  * Chip Temperature - altering reference threshold
  * Humidity - altering reference threshold
  * Gas/Analog sensor values - altering the reference data to test the shortcircuit checking warning.
  * A reset button to revert to the normal values transmitted from the ESP32 board.
* Safety and Alert System: Visual warnings and pop-ups for weather conditions and short-circuits.

## Hardware Architecture (The Breadboard Digital Twin)
The system is powered by an ESP32, which collects data from the following modules:
* MPU6050: Gyroscope and Accelerometer for determining orientation and acceleration.
* BMP280: Barometric pressure, altitude, and chip temperature sensor.
* DHT22: Sensor for external temperature and humidity.
* Gas / Analog Sensor: Detects high spikes in board's surrounding air and flags them as short-circuits.

The hardware design was upgraded from a basic breadboard prototype to a PCB designed in KiCad, featuring optimized routing and safety components.

## Software Architecture (The Drone Digital Twin)
The data is received and processed by a Python script running on the Raspberry Pi (Control Tower). 
The interface uses canvas graphics to simulate an artificial horizon and allows the user to monitor safety limits, including maximum altitude, low pressure thresholds, wet condition risks, and hardware overheating.

## Setup / How to run

### 1. Drone Component (ESP32)
The code inside 'src/main.cpp' is meant to be compiled and uploaded using the Arduino IDE (or the PlatformIO extension).

Make sure you install the following libraries before uploading:
* PubSubClient
* Adafruit MPU6050
* Adafruit BMP280 Library
* DHT sensor library

Update the ssid, password, and mqtt_server variables in the code with your local network credentials.

If you use VS Code with Platformio Extension add the header #include <Arduino.h>.
If you use Arduino IDE save the ESP32 file as .ino.

Make sure you connected the pins as they should!


### 2. Control Tower Component (Dashboard / Monitoring)
The code inside 'dashboard/live_dashboard.py' is a Python script meant to run on the Raspberry Pi (or any PC connected to the same network) to monitor and process the data sent by the ESP32 via MQTT.

Make sure you install the following library before running:

```bash
pip install paho-mqtt