#!/usr/bin/env python3
import os
import time
import threading
import colorsys
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

# Path to RGB zones
RGB_PATH = "/sys/class/leds"

# Detect zones dynamically
def get_zones():
    zones = []
    for entry in os.listdir(RGB_PATH):
        if entry.startswith("hp-wmi::zone"):
            zones.append(entry)
    zones.sort()
    return zones

# Write RGB value to a specific zone
def set_zone_rgb(zone, r, g, b):
    try:
        with open(os.path.join(RGB_PATH, zone, "red"), "w") as f:
            f.write(str(r))
        with open(os.path.join(RGB_PATH, zone, "green"), "w") as f:
            f.write(str(g))
        with open(os.path.join(RGB_PATH, zone, "blue"), "w") as f:
            f.write(str(b))
    except PermissionError:
        messagebox.showerror("Permission Error", "Run this script as root (sudo)!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write to {zone}: {e}")

# Read current RGB of a zone
def get_zone_rgb(zone):
    try:
        r = int(open(os.path.join(RGB_PATH, zone, "red")).read().strip())
        g = int(open(os.path.join(RGB_PATH, zone, "green")).read().strip())
        b = int(open(os.path.join(RGB_PATH, zone, "blue")).read().strip())
        return (r, g, b)
    except Exception:
        return (0, 0, 0)

# Convert HSV to RGB (0-255)
def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r*255), int(g*255), int(b*255)

# Rainbow effect thread
class RainbowEffect(threading.Thread):
    def __init__(self, zones, delay=0.05):
        super().__init__()
        self.zones = zones
        self.delay = delay
        self.running = True

    def run(self):
        hue = 0
        while self.running:
            for i, zone in enumerate(self.zones):
                angle = (hue + i*30) % 360
                r, g, b = hsv_to_rgb(angle/360, 1, 1)
                set_zone_rgb(zone, r, g, b)
            hue = (hue + 5) % 360
            time.sleep(self.delay)

    def stop(self):
        self.running = False

# GUI
class RGBController:
    def __init__(self, master):
        self.master = master
        self.master.title("HP Victus RGB Controller")
        self.zones = get_zones()
        self.effect_thread = None

        self.frames = {}
        self.sliders = {}
        self.color_buttons = {}

        # Build GUI
        for zone in self.zones:
            frame = ttk.LabelFrame(master, text=zone)
            frame.pack(padx=10, pady=5, fill="x")
            self.frames[zone] = frame

            # Sliders
            self.sliders[zone] = {}
            for color in ["Red", "Green", "Blue"]:
                ttk.Label(frame, text=color).pack(side="left", padx=5)
                slider = ttk.Scale(frame, from_=0, to=255, orient="horizontal")
                slider.pack(side="left", padx=5)
                self.sliders[zone][color.lower()] = slider

            # Color picker
            btn = ttk.Button(frame, text="Pick Color", command=lambda z=zone: self.pick_color(z))
            btn.pack(side="left", padx=5)
            self.color_buttons[zone] = btn

            # Apply button
            apply_btn = ttk.Button(frame, text="Apply", command=lambda z=zone: self.apply_zone(z))
            apply_btn.pack(side="left", padx=5)

        # Global controls
        control_frame = ttk.Frame(master)
        control_frame.pack(padx=10, pady=10)

        ttk.Button(control_frame, text="Apply All Zones", command=self.apply_all).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Start Rainbow", command=self.start_rainbow).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Stop Rainbow", command=self.stop_rainbow).pack(side="left", padx=5)

        # Load initial values
        self.load_current_values()

    def load_current_values(self):
        for zone in self.zones:
            r, g, b = get_zone_rgb(zone)
            self.sliders[zone]["red"].set(r)
            self.sliders[zone]["green"].set(g)
            self.sliders[zone]["blue"].set(b)

    def pick_color(self, zone):
        color = colorchooser.askcolor()
        if color[0]:
            r, g, b = map(int, color[0])
            self.sliders[zone]["red"].set(r)
            self.sliders[zone]["green"].set(g)
            self.sliders[zone]["blue"].set(b)
            self.apply_zone(zone)

    def apply_zone(self, zone):
        r = int(self.sliders[zone]["red"].get())
        g = int(self.sliders[zone]["green"].get())
        b = int(self.sliders[zone]["blue"].get())
        set_zone_rgb(zone, r, g, b)

    def apply_all(self):
        for zone in self.zones:
            self.apply_zone(zone)

    def start_rainbow(self):
        if self.effect_thread and self.effect_thread.is_alive():
            return
        self.effect_thread = RainbowEffect(self.zones)
        self.effect_thread.start()

    def stop_rainbow(self):
        if self.effect_thread:
            self.effect_thread.stop()
            self.effect_thread.join()
            self.effect_thread = None
            self.load_current_values()

if __name__ == "__main__":
    root = tk.Tk()
    app = RGBController(root)
    root.mainloop()
