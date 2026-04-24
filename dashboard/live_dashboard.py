import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import font

data = {
    "gx": 0.0, "gy": 0.0, "gz": 0.0,
    "ax": 0.0, "ay": 0.0, "az": 0.0,
    "temp": 0.0, "pres": 0.0, "alt": 0.0
}

def on_message(client, userdata, msg):
    global data
    try:
        payload = msg.payload.decode()
        parts = payload.split()
        
        val_x = float(parts[0].split(':')[1])
        val_y = float(parts[1].split(':')[1])
        val_z = float(parts[2].split(':')[1])
        
        data["gx"], data["gy"], data["gz"] = val_x, val_y, val_z
        data["ax"], data["ay"], data["az"] = val_x, val_y, val_z
    except Exception:
        pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("10.42.0.1", 1883)
client.subscribe("esp32")
client.loop_start()

root = tk.Tk()
root.title("HUD Telemetrie ESP32")
width, height = 1000, 600
root.geometry(f"{width}x{height}")
root.configure(bg='#1e272e')

title_font = font.Font(family="Helvetica", size=14, weight="bold")
value_font = font.Font(family="Courier", size=24, weight="bold")
label_font = font.Font(family="Helvetica", size=10)

canvas = tk.Canvas(root, width=width, height=height, bg="#1e272e", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

center_x, center_y = width // 2, height // 2

canvas.create_line(0, center_y, width, center_y, fill="#485460", dash=(2, 4))
canvas.create_line(center_x, 0, center_x, height, fill="#485460", dash=(2, 4))
canvas.create_oval(center_x - 150, center_y - 150, center_x + 150, center_y + 150, outline="#485460", dash=(2, 4))

dot = canvas.create_oval(center_x - 15, center_y - 15, center_x + 15, center_y + 15, fill="#0be881", outline="#ffffff", width=2)

canvas.create_text(40, 40, text="GIROSCOP (°/s)", fill="#00d8d6", font=title_font, anchor="w")
txt_gx = canvas.create_text(40, 80, text="X:  0.00", fill="white", font=value_font, anchor="w")
txt_gy = canvas.create_text(40, 120, text="Y:  0.00", fill="white", font=value_font, anchor="w")
txt_gz = canvas.create_text(40, 160, text="Z:  0.00", fill="white", font=value_font, anchor="w")

canvas.create_text(40, 240, text="ACCELEROMETRU (m/s²)", fill="#0fbcf9", font=title_font, anchor="w")
txt_ax = canvas.create_text(40, 280, text="X:  0.00", fill="white", font=value_font, anchor="w")
txt_ay = canvas.create_text(40, 320, text="Y:  0.00", fill="white", font=value_font, anchor="w")
txt_az = canvas.create_text(40, 360, text="Z:  0.00", fill="white", font=value_font, anchor="w")

canvas.create_text(width - 40, 40, text="MEDIU & ATMOSFERĂ", fill="#ffdd59", font=title_font, anchor="e")
canvas.create_text(width - 40, 90, text="Temperatură (°C)", fill="#d2dae2", font=label_font, anchor="e")
txt_temp = canvas.create_text(width - 40, 120, text="0.0", fill="#ff5e57", font=value_font, anchor="e")

canvas.create_text(width - 40, 180, text="Presiune (hPa)", fill="#d2dae2", font=label_font, anchor="e")
txt_pres = canvas.create_text(width - 40, 210, text="0.0", fill="#0be881", font=value_font, anchor="e")

canvas.create_text(width - 40, 270, text="Altitudine (m)", fill="#d2dae2", font=label_font, anchor="e")
txt_alt = canvas.create_text(width - 40, 300, text="0.0", fill="#0fbcf9", font=value_font, anchor="e")

def map_value(x, in_min, in_max, out_min, out_max):
    x = max(min(x, in_max), in_min)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def update_gui():
    canvas.itemconfig(txt_gx, text=f"X: {data['gx']:>6.2f}")
    canvas.itemconfig(txt_gy, text=f"Y: {data['gy']:>6.2f}")
    canvas.itemconfig(txt_gz, text=f"Z: {data['gz']:>6.2f}")
    
    canvas.itemconfig(txt_ax, text=f"X: {data['ax']:>6.2f}")
    canvas.itemconfig(txt_ay, text=f"Y: {data['ay']:>6.2f}")
    canvas.itemconfig(txt_az, text=f"Z: {data['az']:>6.2f}")
    
    limita_sensibilitate = 50
    
    target_x = map_value(data['ax'], -limita_sensibilitate, limita_sensibilitate, 0, width)
    target_y = map_value(data['ay'], -limita_sensibilitate, limita_sensibilitate, 0, height)
    r = map_value(data['az'], -limita_sensibilitate, limita_sensibilitate, 5, 50) 
    
    canvas.coords(dot, target_x - r, target_y - r, target_x + r, target_y + r)
    root.after(50, update_gui)

update_gui()
root.mainloop()