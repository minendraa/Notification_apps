import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from plyer import notification
import threading
import time
import pygame

# 🔊 Sound function using pygame
def play_alarm_sound():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("alarm.mp3")  # Use your actual mp3 or wav file here
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except Exception as e:
        print(f"⚠️ Error playing sound: {e}")

# 🔔 Notification function
def show_notification():
    notification.notify(
        title="⏰ Alarm!",
        message="Time's up!",
        timeout=10
    )

# 🕑 Alarm clock loop in a thread
def alarm_clock(alarm_time):
    while True:
        current_time = datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            print("🔔 Alarm triggered!")
            show_notification()
            play_alarm_sound()
            break
        time.sleep(10)

# 📅 Set alarm and validate input
def set_alarm():
    hour = hour_var.get()
    minute = minute_var.get()
    period = period_var.get()

    if not hour or not minute:
        messagebox.showerror("Input Error", "Please select hour and minute.")
        return

    try:
        alarm_input = f"{hour}:{minute} {period}"
        alarm_time = datetime.strptime(alarm_input, "%I:%M %p").strftime("%H:%M")
        threading.Thread(target=alarm_clock, args=(alarm_time,), daemon=True).start()
        messagebox.showinfo("Alarm Set", f"Alarm is set for {alarm_input}")
    except ValueError:
        messagebox.showerror("Format Error", "Invalid time format.")

# 🖼️ GUI Setup
root = tk.Tk()
root.title("Alarm Clock")
root.geometry("300x250")
root.resizable(False, False)

tk.Label(root, text="Set Alarm Time", font=("Arial", 16)).pack(pady=10)

frame = tk.Frame(root)
frame.pack()

# Time input spinboxes
hour_var = tk.StringVar()
minute_var = tk.StringVar()
period_var = tk.StringVar(value="AM")

hour_spin = tk.Spinbox(frame, from_=1, to=12, width=5, textvariable=hour_var, format="%02.0f", font=("Arial", 12))
minute_spin = tk.Spinbox(frame, from_=0, to=59, width=5, textvariable=minute_var, format="%02.0f", font=("Arial", 12))
period_spin = tk.Spinbox(frame, values=("AM", "PM"), width=5, textvariable=period_var, font=("Arial", 12))

hour_spin.grid(row=0, column=0, padx=5)
minute_spin.grid(row=0, column=1, padx=5)
period_spin.grid(row=0, column=2, padx=5)

# Set alarm button
tk.Button(root, text="Set Alarm", command=set_alarm, font=("Arial", 12), bg="green", fg="white").pack(pady=20)

# Exit button
tk.Button(root, text="Exit", command=root.destroy, font=("Arial", 10)).pack()

root.mainloop()
