# gui.py

import tkinter as tk
from tkinter import Label


class GUI:
    def __init__(self):
        """Settings window"""
        self.top = tk.Tk()
        self.top.title("Simulation")
        self.top.geometry("1080x710")
        self.top.resizable(width=False, height=False)

        """Set canvas"""
        self.c = tk.Canvas(self.top, width=1080, height=680, bg="#A9A9A9")
        self.c.pack()

        self.label = Label(self.top, text="Time = 0.0 s")
        self.label.pack()

        self.colors = ["red", "green", "blue", "orange"]  # Colors for each quadrant

    def update_time(self, _time):
        """Update display time"""
        self.label['text'] = "Simulation Time: \t" + _time + "\t s"

    def add_oval(self, x, y, r, tag, p_type):
        """Draw circle"""
        color = self.colors[p_type - 1]  # Select color based on quadrant
        self.c.create_oval(x - r, y - r, x + r, y + r, fill=color, tag=tag)

    def add_circle(self, x, y, r, tag, p_type):
        """Draw circle"""
        color = self.colors[p_type - 1]  # Select color based on quadrant
        self.c.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2, tag=tag)

    def del_oval(self, oval_tag):
        """Delete circle"""
        self.c.delete(oval_tag)

    def update_gui(self):
        """Update GUI"""
        self.top.update()
        self.c.update()

    def start(self):
        """Start GUI"""
        self.top.mainloop()



#if __name__ == "__main__":
  # gui = GUI()
   # gui.start()

