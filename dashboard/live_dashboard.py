import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import font
import time

data = {
    "gx": 0.0, "gy": 0.0, "gz": 0.0,
    "ax": 0.0, "ay": 0.0, "az": 0.0,
    "roll": 0.0, "pitch": 0.0,
    "temp": 0.0, "pres": 0.0, "alt": 0.0
}

home_alt = None
last_stable_val = 0.0
stable_start_time = time.time()
smooth_alt_y = 100.0 
alpha = 0.15 

def on_message(client, userdata, msg):
    global data, home_alt
    try:
        payload = msg.payload.decode()
        parts = payload.replace(':', ' ').replace(',', ' ').split()
        
        if len(parts) >= 22:
            data["ax"] = float(parts[1])
            data["ay"] = float(parts[3])
            data["az"] = float(parts[5])
            data["gx"] = float(parts[7])
            data["gy"] = float(parts[9])
            data["gz"] = float(parts[11])
            data["roll"] = float(parts[13])
            data["pitch"] = float(parts[15])
            data["pres"] = float(parts[17])
            data["temp"] = float(parts[19])
            data["alt"] = float(parts[21])
            
            if home_alt is None:
                home_alt = data["alt"]
    except Exception:
        pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("192.168.137.219", 1883)
client.subscribe("esp32")
client.loop_start()

root = tk.Tk()
root.title("Cockpit Telemetrie ESP32")
root.geometry("1100x600")
root.configure(bg='#1e272e')

title_font = font.Font(family="Helvetica", size=13, weight="bold")
value_font = font.Font(family="Courier", size=20, weight="bold")
label_font = font.Font(family="Helvetica", size=9, weight="bold")

left_frame = tk.Frame(root, bg='#1e272e', width=250)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=30, pady=20)
center_frame = tk.Frame(root, bg='#1e272e')
center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right_frame = tk.Frame(root, bg='#1e272e', width=250)
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=30, pady=20)

tk.Label(left_frame, text="GIROSCOP", fg="#00d8d6", bg='#1e272e', font=title_font).pack(pady=(0, 5))
lbl_gx = tk.Label(left_frame, text="X: 0.00", fg="white", bg='#1e272e', font=value_font); lbl_gx.pack()
lbl_gy = tk.Label(left_frame, text="Y: 0.00", fg="white", bg='#1e272e', font=value_font); lbl_gy.pack()
lbl_gz = tk.Label(left_frame, text="Z: 0.00", fg="white", bg='#1e272e', font=value_font); lbl_gz.pack()

tk.Label(left_frame, text="ACCELEROMETRU", fg="#0fbcf9", bg='#1e272e', font=title_font).pack(pady=(30, 5))
lbl_ax = tk.Label(left_frame, text="X: 0.00", fg="white", bg='#1e272e', font=value_font); lbl_ax.pack()
lbl_ay = tk.Label(left_frame, text="Y: 0.00", fg="white", bg='#1e272e', font=value_font); lbl_ay.pack()
lbl_az = tk.Label(left_frame, text="Z: 0.00", fg="white", bg='#1e272e', font=value_font); lbl_az.pack()

tk.Label(right_frame, text="ATMOSFERĂ", fg="#ffdd59", bg='#1e272e', font=title_font).pack(pady=(0, 5))
lbl_temp = tk.Label(right_frame, text="0.0°C", fg="#ff5e57", bg='#1e272e', font=value_font); lbl_temp.pack()
lbl_pres = tk.Label(right_frame, text="0.0 hPa", fg="#0be881", bg='#1e272e', font=value_font); lbl_pres.pack()

tk.Label(right_frame, text="ALTITUDE TAPE (REL)", fg="#d2dae2", bg='#1e272e', font=label_font).pack(pady=(30, 5))
alt_canvas = tk.Canvas(right_frame, width=70, height=200, bg="#2f3640", highlightthickness=1, highlightbackground="#0fbcf9")
alt_canvas.pack()
for i in range(20, 200, 40):
    alt_canvas.create_line(35, i, 55, i, fill="#718093")
alt_canvas.create_polygon(5, 100, 15, 93, 15, 107, fill="#0fbcf9")
alt_marker = alt_canvas.create_rectangle(20, 95, 65, 105, fill="#0fbcf9", outline="white")

lbl_alt_rel = tk.Label(right_frame, text="+0.00m", fg="#0fbcf9", bg='#1e272e', font=value_font); lbl_alt_rel.pack(pady=5)
lbl_alt_abs = tk.Label(right_frame, text="BASE: 0.0m", fg="#718093", bg='#1e272e', font=label_font); lbl_alt_abs.pack()

canvas_size = 400
center_x, center_y = canvas_size // 2, canvas_size // 2
canvas = tk.Canvas(center_frame, width=canvas_size, height=canvas_size, bg="#2f3640", highlightthickness=2, highlightbackground="#0fbcf9")
canvas.pack(pady=50)
canvas.create_line(0, center_y, canvas_size, center_y, fill="#718093", dash=(4, 4))
canvas.create_line(center_x, 0, center_x, canvas_size, fill="#718093", dash=(4, 4))
canvas.create_oval(50, 50, 350, 350, outline="#485460", dash=(2, 2))

dot_radius = 11
dot = canvas.create_oval(center_x-dot_radius, center_y-dot_radius, center_x+dot_radius, center_y+dot_radius, fill="#0be881", outline="white", width=2)

def map_value(x, in_min, in_max, out_min, out_max):
    x = max(min(x, in_max), in_min)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def update_gui():
    global home_alt, last_stable_val, stable_start_time, smooth_alt_y
    if home_alt is None:
        root.after(50, update_gui)
        return
    curr_alt = data["alt"]
    if abs(curr_alt - last_stable_val) > 0.15:
        last_stable_val = curr_alt
        stable_start_time = time.time()
    else:
        if time.time() - stable_start_time > 10:
            home_alt = curr_alt
            stable_start_time = time.time()
    lbl_gx.config(text=f"X: {data['gx']:>6.2f}")
    lbl_gy.config(text=f"Y: {data['gy']:>6.2f}")
    lbl_gz.config(text=f"Z: {data['gz']:>6.2f}")
    lbl_ax.config(text=f"X: {data['ax']:>6.2f}")
    lbl_ay.config(text=f"Y: {data['ay']:>6.2f}")
    lbl_az.config(text=f"Z: {data['az']:>6.2f}")
    lbl_temp.config(text=f"{data['temp']:.1f}°C")
    lbl_pres.config(text=f"{data['pres']:.1f} hPa")
    rel_alt = curr_alt - home_alt
    lbl_alt_rel.config(text=f"{rel_alt:+.2f}m")
    lbl_alt_abs.config(text=f"BASE: {home_alt:.1f}m")
    tx = map_value(data["ax"], -1.0, 1.0, canvas_size, 0)
    ty = map_value(data["ay"], -1.0, 1.0, canvas_size, 0)
    canvas.coords(dot, tx-dot_radius, ty-dot_radius, tx+dot_radius, ty+dot_radius)
    target_y = map_value(rel_alt, -3.0, 3.0, 180, 20)
    smooth_alt_y = (smooth_alt_y * (1 - alpha)) + (target_y * alpha)
    alt_canvas.coords(alt_marker, 20, smooth_alt_y - 5, 65, smooth_alt_y + 5)
    root.after(30, update_gui)

update_gui()
root.mainloop()