import tkinter as tk
from tkinter import ttk
import time
import threading
import winsound


class MetronomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metronome")
        self.root.geometry("600x400")
        self.root.configure(bg='#AEC6CF')
        self.is_running = False
        self.tempo = 60
        self.direction = 1
        self.create_widgets()
        style = ttk.Style()
        style.configure('TFrame', background='#FFFFF0')


    def create_widgets(self):
        self.tempo_label = ttk.Label(self.root, text=str(self.tempo), font=("Helvetica", 48), background='#AEC6CF')
        self.tempo_label.pack(pady=20)

        button_frame = ttk.Frame(self.root, padding=10, style='TFrame')
        button_frame.pack()

        self.decrease_btn_1 = ttk.Button(button_frame, text="-1", command=lambda: self.change_tempo(-1))
        self.decrease_btn_1.grid(row=0, column=0, padx=5)

        self.increase_btn_1 = ttk.Button(button_frame, text="+1", command=lambda: self.change_tempo(1))
        self.increase_btn_1.grid(row=0, column=1, padx=5)

        self.decrease_btn_5 = ttk.Button(button_frame, text="-5", command=lambda: self.change_tempo(-5))
        self.decrease_btn_5.grid(row=0, column=2, padx=5)

        self.increase_btn_5 = ttk.Button(button_frame, text="+5", command=lambda: self.change_tempo(5))
        self.increase_btn_5.grid(row=0, column=3, padx=5)

        self.slider = ttk.Scale(self.root, from_=1, to_=500, orient="horizontal", command=self.slider_changed)
        self.slider.set(self.tempo)
        self.slider.pack(fill="x", pady=20)

        self.canvas = tk.Canvas(self.root, width=200, height=50, bg='#AEC6CF', highlightthickness=0)
        self.canvas.pack(pady=20)
        self.line = self.canvas.create_line(0, 25, 200, 25, fill='red', width=5)
        self.circle = self.canvas.create_oval(90, 15, 110, 35, fill='red')

        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack()

        self.start_btn = ttk.Button(control_frame, text="Start", command=self.start_metronome)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_metronome)
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.quit_btn = ttk.Button(control_frame, text="Quit", command=self.root.quit)
        self.quit_btn.grid(row=0, column=2, padx=5)

    def change_tempo(self, value):
        self.tempo += value
        self.tempo = max(30, min(self.tempo, 240))
        self.tempo_label.config(text=str(self.tempo))
        self.slider.set(self.tempo)

    def slider_changed(self, event):
        self.tempo = int(float(self.slider.get()))
        self.tempo_label.config(text=str(self.tempo))

    def start_metronome(self):
        if not self.is_running:
            self.is_running = True
            self.metronome_thread = threading.Thread(target=self.run_metronome)
            self.metronome_thread.start()

    def stop_metronome(self):
        self.is_running = False

    def run_metronome(self):
        while self.is_running:
            self.move_circle()
            time.sleep(60 / self.tempo / 50)  # Adjust for smooth movement

    def move_circle(self):
        coords = self.canvas.coords(self.circle)
        if coords[2] >= 200 or coords[0] <= 0:  # If the circle hits the edge, change direction
            self.direction *= -1
            self.play_tick()
        self.canvas.move(self.circle, self.direction * 4, 0)
        self.root.update()

    def play_tick(self):
        winsound.Beep(1000, 100)  # 1000 Hz frequency, 100 ms duration


if __name__ == "__main__":
    root = tk.Tk()
    app = MetronomeApp(root)
    root.mainloop()
