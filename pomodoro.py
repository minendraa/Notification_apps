import tkinter as tk
from tkinter import ttk, messagebox
import pygame
from plyer import notification
import os

# --- UI Constants ---
COLOR_BG = "#1C1C1C"
COLOR_FG = "#FFFFFF"
COLOR_FOCUS = "#FF4500"
COLOR_BREAK = "#4682B4"
COLOR_PAUSED = "#808080"
FONT_LARGE = ("Helvetica", 48, "bold")
FONT_MEDIUM = ("Helvetica", 16)
FONT_SMALL = ("Helvetica", 12)
FONT_INPUT = ("Helvetica", 10)

# --- Sound Setup ---
def setup_sound():
    if not os.path.exists("audio.mp3"):
        messagebox.showwarning("Audio File Missing", "audio.mp3 not found. Notifications will be silent.")
    try:
        pygame.mixer.init()
    except Exception as e:
        messagebox.showerror("Sound Error", f"Could not initialize sound mixer: {e}")

def play_sound():
    try:
        pygame.mixer.music.load("audio.mp3")
        pygame.mixer.music.play(loops=-1)  # Loop music during break
    except Exception as e:
        print(f"Error playing sound: {e}")

def stop_sound():
    try:
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"Error stopping sound: {e}")

def show_notification(title, message):
    try:
        notification.notify(title=title, message=message, app_name="Pomodoro Timer", timeout=10)
    except Exception as e:
        print(f"Error showing notification: {e}")

# --- Pomodoro App ---
class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        self.master.title("🍅 Enhanced Pomodoro")
        self.master.config(padx=20, pady=20, bg=COLOR_BG)
        self.master.resizable(False, False)

        self.work_duration = 25 * 60
        self.break_duration = 5 * 60

        self.remaining_seconds = self.work_duration
        self.is_running = False
        self.is_break = False
        self.session_count = 0
        self.timer_id = None

        self.create_widgets()
        self.reset_timer()

    def create_widgets(self):
        self.status_label = tk.Label(self.master, text="Ready", font=FONT_MEDIUM, bg=COLOR_BG, fg=COLOR_FG)
        self.status_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        self.timer_label = tk.Label(self.master, text="25:00", font=FONT_LARGE, bg=COLOR_BG, fg=COLOR_FG)
        self.timer_label.grid(row=1, column=0, columnspan=3, pady=10)

        style = ttk.Style()
        style.configure("TButton", font=FONT_SMALL, padding=10)

        self.start_button = ttk.Button(self.master, text="▶️ Start", command=self.start_timer)
        self.start_button.grid(row=2, column=0, padx=5, pady=20)

        self.pause_button = ttk.Button(self.master, text="⏸️ Pause", command=self.pause_timer)
        self.pause_button.grid(row=2, column=1, padx=5, pady=20)

        self.reset_button = ttk.Button(self.master, text="🔄 Reset", command=self.reset_timer)
        self.reset_button.grid(row=2, column=2, padx=5, pady=20)

        self.session_label = tk.Label(self.master, text="✅ Sessions: 0", font=FONT_MEDIUM, bg=COLOR_BG, fg=COLOR_FG)
        self.session_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        self.set_time_button = ttk.Button(self.master, text="🕒 Set Custom Time", command=self.open_time_setup_window)
        self.set_time_button.grid(row=4, column=0, columnspan=3, pady=(10, 0))

    def open_time_setup_window(self):
        if self.is_running:
            messagebox.showinfo("Not Allowed", "Pause the timer before setting custom time.")
            return

        window = tk.Toplevel(self.master)
        window.title("Set Custom Time")
        window.config(padx=20, pady=20, bg=COLOR_BG)
        window.resizable(False, False)

        # Focus Time
        tk.Label(window, text="Focus Time:", bg=COLOR_BG, fg=COLOR_FG).grid(row=0, column=0, sticky="e")
        focus_min = tk.Entry(window, width=5)
        focus_min.insert(0, str(self.work_duration // 60))
        focus_min.grid(row=0, column=1)
        tk.Label(window, text="min", bg=COLOR_BG, fg=COLOR_FG).grid(row=0, column=2)

        focus_sec = tk.Entry(window, width=5)
        focus_sec.insert(0, str(self.work_duration % 60))
        focus_sec.grid(row=0, column=3)
        tk.Label(window, text="sec", bg=COLOR_BG, fg=COLOR_FG).grid(row=0, column=4, sticky="w")

        # Break Time
        tk.Label(window, text="Break Time:", bg=COLOR_BG, fg=COLOR_FG).grid(row=1, column=0, sticky="e", pady=5)
        break_min = tk.Entry(window, width=5)
        break_min.insert(0, str(self.break_duration // 60))
        break_min.grid(row=1, column=1)
        tk.Label(window, text="min", bg=COLOR_BG, fg=COLOR_FG).grid(row=1, column=2)

        break_sec = tk.Entry(window, width=5)
        break_sec.insert(0, str(self.break_duration % 60))
        break_sec.grid(row=1, column=3)
        tk.Label(window, text="sec", bg=COLOR_BG, fg=COLOR_FG).grid(row=1, column=4, sticky="w")

        def apply():
            try:
                fmin = int(focus_min.get())
                fsec = int(focus_sec.get())
                bmin = int(break_min.get())
                bsec = int(break_sec.get())

                if fmin < 0 or fsec < 0 or bmin < 0 or bsec < 0:
                    raise ValueError("Negative values")

                self.work_duration = fmin * 60 + fsec
                self.break_duration = bmin * 60 + bsec
                self.reset_timer()
                window.destroy()
                messagebox.showinfo("Updated", f"Focus: {fmin} min {fsec} sec\nBreak: {bmin} min {bsec} sec")

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid whole numbers.")

        apply_btn = ttk.Button(window, text="Apply", command=apply)
        apply_btn.grid(row=2, column=0, columnspan=5, pady=10)

    def start_timer(self):
        if self.is_running:
            return
        self.is_running = True

        if not self.is_break:
            self.status_label.config(text="Focus Time", fg=COLOR_FOCUS)
        else:
            self.status_label.config(text="Break Time", fg=COLOR_BREAK)

        stop_sound()
        self.update_button_states()
        self.countdown()

    def pause_timer(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
        stop_sound()
        self.status_label.config(text="Paused", fg=COLOR_PAUSED)
        self.update_button_states()

    def reset_timer(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
        stop_sound()
        self.is_running = False
        self.is_break = False
        self.session_count = 0
        self.remaining_seconds = self.work_duration
        self.status_label.config(text="Ready to Start", fg=COLOR_FOCUS)
        self.session_label.config(text=f"✅ Sessions: {self.session_count}")
        self.update_timer_display()
        self.update_button_states()

    def countdown(self):
        if not self.is_running:
            return

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_timer_display()
            self.timer_id = self.master.after(1000, self.countdown)
        else:
            self.switch_mode()

    def switch_mode(self):
        stop_sound()  # stop any sound before switching modes

        if not self.is_break:
            # Switching from focus to break
            self.is_break = True
            self.session_count += 1
            self.remaining_seconds = self.break_duration
            self.status_label.config(text="Break Time", fg=COLOR_BREAK)
            self.session_label.config(text=f"✅ Sessions: {self.session_count}")
            play_sound()  # play music during break
            show_notification("Break Time!", f"Take a {self.break_duration // 60} min {self.break_duration % 60} sec break.")
        else:
            # Switching from break to focus
            self.is_break = False
            self.remaining_seconds = self.work_duration
            self.status_label.config(text="Focus Time", fg=COLOR_FOCUS)
            stop_sound()  # stop the break music
            show_notification("Back to Work!", f"Time to focus for {self.work_duration // 60} min {self.work_duration % 60} sec.")

        self.update_timer_display()
        self.timer_id = self.master.after(1000, self.countdown)

    def update_timer_display(self):
        mins, secs = divmod(self.remaining_seconds, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

    def update_button_states(self):
        is_running = self.is_running
        self.start_button.config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.set_time_button.config(state=tk.DISABLED if is_running else tk.NORMAL)

# --- Run App ---
if __name__ == "__main__":
    setup_sound()
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
