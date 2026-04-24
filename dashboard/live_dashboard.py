import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import font
import time

data = {
    "gx": 0.0, "gy": 0.0, "gz": 0.0,
    "ax": 0.0, "ay": 0.0, "az": 0.0,
    "roll": 0.0, "pitch": 0.0,
    "temp": 0.0, "pres": 0.0, "alt": 0.0,
    "tempOut": 0.0, "umid": 0.0, "gaz": 0.0
}

home_alt = None
last_stable_val = 0.0
stable_start_time = time.time()
smooth_alt_y = 100.0 
current_offset = 0.0 
alpha = 0.15 
temp_offset = 0.0
hum_offset = 0.0
pres_offset = 0.0  
settings_window = None
current_hover = None

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
            if len(parts) >= 28:
                data["tempOut"] = float(parts[23])
                data["umid"] = float(parts[25])
                data["gaz"] = float(parts[27])

            if home_alt is None:
                home_alt = data["alt"]
    except Exception:
        pass

def apply_settings(off_val, temp_sim_val, hum_sim_val, pres_sim_val):
    global home_alt, stable_start_time, current_offset, temp_offset, hum_offset, pres_offset
    try:
        current_offset = float(off_val)
        home_alt = data["alt"] - current_offset
        temp_offset = float(temp_sim_val) - data["temp"]
        hum_offset = float(hum_sim_val) - data["umid"]
        pres_offset = float(pres_sim_val) - data["pres"]
        stable_start_time = time.time()
    except ValueError:
        pass

def open_settings():
    global settings_window
    if settings_window is not None and tk.Toplevel.winfo_exists(settings_window):
        settings_window.lift()
        return

    settings_window = tk.Toplevel(root)
    settings_window.title("Panou Setari")
    settings_window.geometry("350x520")  
    settings_window.configure(bg='#1e272e')

    tk.Label(settings_window, text="SIMULARE ALTITUDINE (m)", fg="#0fbcf9", bg='#1e272e', font=label_font).pack(pady=(20, 5))
    off_entry = tk.Entry(settings_window, font=label_font, width=15, bg="#2f3640", fg="white", justify="center")
    off_entry.insert(0, str(current_offset))
    off_entry.pack()

    tk.Label(settings_window, text="LIMITA ALERTA ALTITUDINE (m)", fg="#0fbcf9", bg='#1e272e', font=label_font).pack(pady=(20, 5))
    tk.Entry(settings_window, textvariable=max_alt_var, font=label_font, width=15, bg="#2f3640", fg="white", justify="center").pack()

    tk.Label(settings_window, text="SIMULARE PRESIUNE (hPa)", fg="#0fbcf9", bg='#1e272e', font=label_font).pack(pady=(20, 5))
    pres_entry = tk.Entry(settings_window, font=label_font, width=15, bg="#2f3640", fg="white", justify="center")
    pres_entry.insert(0, f"{(data['pres'] + pres_offset):.1f}")
    pres_entry.pack()

    tk.Label(settings_window, text="SIMULARE TEMP CHIP (°C)", fg="#0fbcf9", bg='#1e272e', font=label_font).pack(pady=(20, 5))
    temp_entry = tk.Entry(settings_window, font=label_font, width=15, bg="#2f3640", fg="white", justify="center")
    temp_entry.insert(0, f"{(data['temp'] + temp_offset):.1f}")
    temp_entry.pack()

    tk.Label(settings_window, text="SIMULARE UMIDITATE (%)", fg="#0fbcf9", bg='#1e272e', font=label_font).pack(pady=(20, 5))
    hum_entry = tk.Entry(settings_window, font=label_font, width=15, bg="#2f3640", fg="white", justify="center")
    hum_entry.insert(0, f"{(data['umid'] + hum_offset):.1f}")
    hum_entry.pack()

    tk.Button(settings_window, text="APLICA MODIFICARI", 
              command=lambda: apply_settings(off_entry.get(), temp_entry.get(), hum_entry.get(), pres_entry.get()), 
              font=label_font, bg="#0fbcf9", fg="black").pack(pady=20)

def enter_hover(status_name): 
    global current_hover
    current_hover = status_name

def leave_hover(event): 
    global current_hover
    current_hover = None

def map_value(x, in_min, in_max, out_min, out_max):
    x = max(min(x, in_max), in_min)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("192.168.137.219", 1883)
client.subscribe("esp32")
client.loop_start()

root = tk.Tk()
root.title("Cockpit Telemetrie ESP32")
win_w, win_h = 1100, 780
root.geometry(f"{win_w}x{win_h}")
root.configure(bg='#1e272e')

title_font = font.Font(family="Helvetica", size=13, weight="bold")
value_font = font.Font(family="Courier", size=20, weight="bold")
label_font = font.Font(family="Helvetica", size=9, weight="bold")
warn_font = font.Font(family="Helvetica", size=15, weight="bold")
hover_font = font.Font(family="Helvetica", size=14, weight="bold") 

cx, cy = win_w // 2, win_h // 2
main_canvas = tk.Canvas(root, width=win_w, height=win_h, bg='#1e272e', highlightthickness=0)
main_canvas.place(x=0, y=0, relwidth=1, relheight=1)

main_canvas.create_line(0, cy, win_w, cy, fill="#2f3640", dash=(4, 4), width=2)
main_canvas.create_line(cx, 0, cx, win_h, fill="#2f3640", dash=(4, 4), width=2)
main_canvas.create_oval(cx - 150, cy - 150, cx + 150, cy + 150, outline="#2f3640", dash=(2, 2), width=2)
main_canvas.create_oval(cx - 300, cy - 300, cx + 300, cy + 300, outline="#2f3640", dash=(2, 2), width=2)

dot_radius = 12
dot = main_canvas.create_oval(cx-dot_radius, cy-dot_radius, cx+dot_radius, cy+dot_radius, fill="#0be881", outline="white", width=2)

main_canvas.create_text(40, 40, text="GIROSCOP", fill="#00d8d6", font=title_font, anchor="w")
txt_gx = main_canvas.create_text(40, 70, text="X: 0.00", fill="white", font=value_font, anchor="w")
txt_gy = main_canvas.create_text(40, 100, text="Y: 0.00", fill="white", font=value_font, anchor="w")
txt_gz = main_canvas.create_text(40, 130, text="Z: 0.00", fill="white", font=value_font, anchor="w")

main_canvas.create_text(40, 190, text="ACCELEROMETRU", fill="#0fbcf9", font=title_font, anchor="w")
txt_ax = main_canvas.create_text(40, 220, text="X: 0.00", fill="white", font=value_font, anchor="w")
txt_ay = main_canvas.create_text(40, 250, text="Y: 0.00", fill="white", font=value_font, anchor="w")
txt_az = main_canvas.create_text(40, 280, text="Z: 0.00", fill="white", font=value_font, anchor="w")

main_canvas.create_text(40, 340, text="TEMPERATURI", fill="#0fbcf9", font=title_font, anchor="w")
txt_tempOut = main_canvas.create_text(40, 370, text="tempOut: 0.0°C", fill="#ff5e57", font=value_font, anchor="w")
txt_tempChip = main_canvas.create_text(40, 400, text="tempChip: 0.0°C", fill="#ff5e57", font=value_font, anchor="w")

right_x = win_w - 40
main_canvas.create_text(right_x, 40, text="ATMOSFERĂ", fill="#ffdd59", font=title_font, anchor="e")
txt_pres = main_canvas.create_text(right_x, 70, text="0.0 hPa", fill="#0be881", font=value_font, anchor="e")
txt_umid = main_canvas.create_text(right_x, 100, text="0.0 %", fill="#0be881", font=value_font, anchor="e")
txt_gaz = main_canvas.create_text(right_x, 130, text="0.0", fill="#0be881", font=value_font, anchor="e")

main_canvas.create_text(right_x, 190, text="", fill="#d2dae2", font=label_font, anchor="e")
txt_alt_rel = main_canvas.create_text(right_x, 440, text="+0.00m", fill="#0fbcf9", font=value_font, anchor="e")

alt_canvas = tk.Canvas(root, width=70, height=200, bg="#2f3640", highlightthickness=1, highlightbackground="#0fbcf9")
alt_canvas.place(x=right_x - 35, y=210, anchor="n")
for i in range(20, 200, 40):
    alt_canvas.create_line(35, i, 55, i, fill="#718093")
alt_canvas.create_polygon(5, 100, 15, 93, 15, 107, fill="#0fbcf9")
alt_marker = alt_canvas.create_rectangle(20, 95, 65, 105, fill="#0fbcf9", outline="white")

btn_settings = tk.Button(root, text="SETARI & SIMULARE", command=open_settings, font=label_font, bg="#485460", fg="white", padx=10, pady=5)
btn_settings.place(x=right_x, y=480, anchor="e")

max_alt_var = tk.StringVar(value="520.0")

stat_y = win_h - 40
sep_y1, sep_y2 = win_h - 50, win_h - 30

txt_stat_alt = main_canvas.create_text(cx - 300, stat_y, text="ALT: SIGUR", fill="#0be881", font=warn_font, tags="hover_alt")
main_canvas.create_line(cx - 200, sep_y1, cx - 200, sep_y2, fill="#00d8d6", width=2)
txt_stat_pres = main_canvas.create_text(cx - 100, stat_y, text="PRES: SIGUR", fill="#0be881", font=warn_font, tags="hover_pres")
main_canvas.create_line(cx, sep_y1, cx, sep_y2, fill="#00d8d6", width=2)
txt_stat_temp = main_canvas.create_text(cx + 100, stat_y, text="TEMP: SIGUR", fill="#0be881", font=warn_font, tags="hover_temp")
main_canvas.create_line(cx + 200, sep_y1, cx + 200, sep_y2, fill="#00d8d6", width=2)
txt_stat_hum = main_canvas.create_text(cx + 300, stat_y, text="UMID: SIGUR", fill="#0be881", font=warn_font, tags="hover_hum")

main_canvas.tag_bind("hover_alt", "<Enter>", lambda e: enter_hover("ALT"))
main_canvas.tag_bind("hover_alt", "<Leave>", leave_hover)
main_canvas.tag_bind("hover_pres", "<Enter>", lambda e: enter_hover("PRES"))
main_canvas.tag_bind("hover_pres", "<Leave>", leave_hover)
main_canvas.tag_bind("hover_temp", "<Enter>", lambda e: enter_hover("TEMP"))
main_canvas.tag_bind("hover_temp", "<Leave>", leave_hover)
main_canvas.tag_bind("hover_hum", "<Enter>", lambda e: enter_hover("HUM"))
main_canvas.tag_bind("hover_hum", "<Leave>", leave_hover)

txt_hover_desc = main_canvas.create_text(cx, win_h - 90, text="", fill="#d2dae2", font=hover_font)

def update_gui():
    global home_alt, last_stable_val, stable_start_time, smooth_alt_y, current_offset
    if home_alt is None:
        root.after(50, update_gui)
        return
    curr_alt = data["alt"]
    
    if abs(curr_alt - last_stable_val) > 0.15:
        last_stable_val = curr_alt
        stable_start_time = time.time()
    else:
        if time.time() - stable_start_time > 10:
            home_alt = curr_alt - current_offset
            stable_start_time = time.time()
            
    disp_temp = data["temp"] + temp_offset
    disp_hum = data["umid"] + hum_offset
    disp_pres = data["pres"] + pres_offset  
            
    main_canvas.itemconfig(txt_gx, text=f"X: {data['gx']:>6.2f}")
    main_canvas.itemconfig(txt_gy, text=f"Y: {data['gy']:>6.2f}")
    main_canvas.itemconfig(txt_gz, text=f"Z: {data['gz']:>6.2f}")
    main_canvas.itemconfig(txt_ax, text=f"X: {data['ax']:>6.2f}")
    main_canvas.itemconfig(txt_ay, text=f"Y: {data['ay']:>6.2f}")
    main_canvas.itemconfig(txt_az, text=f"Z: {data['az']:>6.2f}")
    main_canvas.itemconfig(txt_tempOut, text=f"tempOut: {data['tempOut']:.1f}°C")
    main_canvas.itemconfig(txt_tempChip, text=f"tempChip: {disp_temp:.1f}°C")
    main_canvas.itemconfig(txt_pres, text=f"{disp_pres:.1f} hPa")
    main_canvas.itemconfig(txt_umid, text=f"{disp_hum:.1f} %")
    main_canvas.itemconfig(txt_gaz, text=f"{data['gaz']:.1f}")
    
    rel_alt = curr_alt - home_alt
    main_canvas.itemconfig(txt_alt_rel, text=f"{rel_alt:+.2f}m")

    orange_color = "#ffa502"
    hover_texts = {"ALT": "", "PRES": "", "TEMP": "", "HUM": ""}
    
    try:
        if rel_alt >= float(max_alt_var.get()):
            main_canvas.itemconfig(txt_stat_alt, text="ALT: PERICOL", fill="#ff5e57")
            hover_texts["ALT"] = "Altitudine critica: A depasit pragul de alerta setat!"
        else:
            main_canvas.itemconfig(txt_stat_alt, text="ALT: SIGUR", fill="#0be881")
            hover_texts["ALT"] = "Altitudine in parametri normali de zbor."

        if disp_pres < 600.0:
            main_canvas.itemconfig(txt_stat_pres, text="PRES: PERICOL", fill="#ff5e57")
            hover_texts["PRES"] = "Presiune critica (<600 hPa). Risc major in functionare."
        elif disp_pres <= 700.0:
            main_canvas.itemconfig(txt_stat_pres, text="PRES: ATENTIE", fill=orange_color)
            hover_texts["PRES"] = "Presiune scazuta (600-700 hPa). Conditii atmosferice nefavorabile."
        else:
            main_canvas.itemconfig(txt_stat_pres, text="PRES: SIGUR", fill="#0be881")
            hover_texts["PRES"] = "Presiune optima (>700 hPa). Senzorul raporteaza conditii bune."

        if disp_temp >= 75.0:
            main_canvas.itemconfig(txt_stat_temp, text="TEMP: PERICOL", fill="#ff5e57")
            hover_texts["TEMP"] = "Supraincalzire cip (>75°C). Risc de daune hardware."
        elif disp_temp >= 60.0:
            main_canvas.itemconfig(txt_stat_temp, text="TEMP: ATENTIE", fill=orange_color)
            hover_texts["TEMP"] = "Temperatura ridicata (60-75°C). Necesita monitorizare."
        else:
            main_canvas.itemconfig(txt_stat_temp, text="TEMP: SIGUR", fill="#0be881")
            hover_texts["TEMP"] = "Temperatura sistemului este stabila si sigura."

        if disp_hum >= 80.0:
            main_canvas.itemconfig(txt_stat_hum, text="UMID: PERICOL", fill="#ff5e57")
            hover_texts["HUM"] = "Umiditate extrema (>80%). Risc de scurtcircuit / condens."
        elif disp_hum >= 60.0:
            main_canvas.itemconfig(txt_stat_hum, text="UMID: ATENTIE", fill=orange_color)
            hover_texts["HUM"] = "Umiditate ridicata (60-80%). Expunere la mediu umed."
        else:
            main_canvas.itemconfig(txt_stat_hum, text="UMID: SIGUR", fill="#0be881")
            hover_texts["HUM"] = "Umiditate in limite acceptabile de functionare."
            
    except ValueError: 
        pass

    if current_hover and current_hover in hover_texts:
        main_canvas.itemconfig(txt_hover_desc, text=hover_texts[current_hover])
    else:
        main_canvas.itemconfig(txt_hover_desc, text="")

    tx = map_value(data["ax"], -1.0, 1.0, cx + 350, cx - 350)
    ty = map_value(data["ay"], -1.0, 1.0, cy + 350, cy - 350)
    main_canvas.coords(dot, tx-dot_radius, ty-dot_radius, tx+dot_radius, ty+dot_radius)
    
    target_y = map_value(rel_alt, current_offset - 3.0, current_offset + 3.0, 180, 20)
    smooth_alt_y = (smooth_alt_y * (1 - alpha)) + (target_y * alpha)
    alt_canvas.coords(alt_marker, 20, smooth_alt_y - 5, 65, smooth_alt_y + 5)
    
    root.after(30, update_gui)

update_gui()
root.mainloop()