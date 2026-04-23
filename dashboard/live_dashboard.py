import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import font

data = {"x": 0.0, "y": 0.0, "z": 0.0}

def on_message(client, userdata, msg):
    global data
    try:
        parts = msg.payload.decode().split()
        data["x"] = float(parts[0].split(':')[1])
        data["y"] = float(parts[1].split(':')[1])
        data["z"] = float(parts[2].split(':')[1])
    except (IndexError, ValueError):
        pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("#")
client.loop_start()

root = tk.Tk()
root.title("ESP32 Monitor")
root.geometry("400x300")
root.configure(bg='#2c3e50')

custom_font = font.Font(family="Helvetica", size=25, weight="bold")
title_font = font.Font(family="Helvetica", size=14)

tk.Label(root, text="LIVE TELEMETRY", fg="white", bg="#2c3e50", font=title_font).pack(pady=20)

lbl_x = tk.Label(root, text="X: 0.00", fg="#e74c3c", bg="#2c3e50", font=custom_font)
lbl_x.pack()
lbl_y = tk.Label(root, text="Y: 0.00", fg="#2ecc71", bg="#2c3e50", font=custom_font)
lbl_y.pack()
lbl_z = tk.Label(root, text="Z: 0.00", fg="#3498db", bg="#2c3e50", font=custom_font)
lbl_z.pack()

def update_gui():
    lbl_x.config(text=f"X: {data['x']:.2f}")
    lbl_y.config(text=f"Y: {data['y']:.2f}")
    lbl_z.config(text=f"Z: {data['z']:.2f}")
    root.after(100, update_gui)

update_gui()
root.mainloop()