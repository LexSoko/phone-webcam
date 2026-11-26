"""Simple Tkinter settings GUI for Phone Webcam."""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import socket
import json
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import socket
from folder import (
    load_json,
    load_config,
    save_config,
    app_dir,
    resource_path
)

class SettingsWindow:
    def __init__(self, default_config: dict):
        self.defaults = default_config
        self.config = load_config(default_config)

        self.root = ttk.Window(themename="darkly")
        self.root.title("Phone Webcam")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
  
        header = ttk.Frame(self.root, padding=16)
        header.pack(fill=X)

        ttk.Label(header, text="Phone Webcam",
                  font=ttk.Font(size=20, weight="bold"),
                  foreground="white").pack(anchor=W)

        ttk.Label(header, text="Stream your phone camera as a webcam on your PC",
                  foreground="#aaa").pack(anchor=W, pady=(0, 16))

  
        card = ttk.Labelframe(self.root, text="Settings", padding=16)
        card.pack(fill=X, padx=16, pady=8)

        self.width_var = tk.StringVar(value=str(self.config["width"]))
        self.height_var = tk.StringVar(value=str(self.config["height"]))
        self.fps_var = tk.StringVar(value=str(self.config["fps"]))
        self.quality_var = tk.StringVar(value=str(self.config["quality"]))

        self._build_row(card, "Resolution", "Width × Height",
                        [self.width_var, self.height_var])
        self._build_row(card, "FPS", "Frames per second",
                        [self.fps_var])
        self._build_row(card, "Quality", "JPEG quality (0.3–1.0)",
                        [self.quality_var])

        apply_btn = ttk.Button(
            self.root,
            text="Apply",
            bootstyle=(SUCCESS, OUTLINE),
            command=self._apply
        )

        self.root.style.configure(
            apply_btn.cget("style"),
            font=("Segoe UI", 11, "bold")
        )

        apply_btn.pack(pady=16)

     
        url_frame = ttk.Frame(self.root, padding=12)
        url_frame.pack(fill=X, padx=16, pady=4)

        ttk.Label(url_frame, text="Open this on your phone:",
                  font=ttk.Font(size=9), foreground="#888").pack(anchor=W)

        self.url_var = tk.StringVar(value=self._get_lan_url())
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var,
                                   font=ttk.Font(family="Consolas", size=11),
                                   state="readonly", bootstyle="secondary")
        self.url_entry.pack(fill=X, pady=4)

       
        ttk.Button(url_frame, text="Copy URL", bootstyle="info-outline",
                   command=self._copy_url).pack(fill=X)

       
        self.status_var = tk.StringVar(value="● Stopped")
        ttk.Label(self.root, textvariable=self.status_var,
                  font=ttk.Font(size=9), foreground="#f0a").pack(pady=8)

       
        ttk.Button(self.root, text="Open config folder",
                   bootstyle="link", command=self._open_config).pack(pady=4)

      
        self.root.after(3000, self._refresh_url)

    def _build_row(self, parent, label, hint, vars_list):
        """A single config row with label, hint, and input fields."""
        row = ttk.Frame(parent)
        row.pack(fill=X, pady=2)

        ttk.Label(row, text=label, width=12, anchor=W,
                  foreground="white").pack(side=LEFT)

        info_frame = ttk.Frame(row)
        info_frame.pack(side=RIGHT, fill=X, expand=True)

        ttk.Label(info_frame, text=hint,
                  foreground="#666", font=ttk.Font(size=8)).pack(anchor=E)

        entries = []
        for v in vars_list:
            e = ttk.Entry(info_frame, textvariable=v, bootstyle="secondary")
            e.pack(fill=X, side=TOP, pady=2)
            entries.append(e)

    def _apply(self):

        try:
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            f = int(self.fps_var.get())
            q = float(self.quality_var.get())

        except ValueError:
            messagebox.showerror(
                "Invalid",
                "All fields must be valid numbers."
            )
            return

        if w <= 0 or h <= 0:
            messagebox.showerror(
                "Invalid resolution",
                "Width and height must be positive."
            )
            return

        if f <= 0:
            messagebox.showerror(
                "Invalid FPS",
                "FPS must be positive."
            )
            return

        if not 0.3 <= q <= 1.0:
            messagebox.showerror(
                "Invalid quality",
                "Quality must be between 0.3 and 1.0."
            )
            return

        new_config = {
            **self.config,
            "width": w,
            "height": h,
            "fps": f,
            "quality": q
        }

        try:
            save_config(new_config)
        except OSError as e:
            messagebox.showerror("Save failed", str(e))
            return

        self.config = new_config

        self.status_var.set(
            "● Settings saved — restart phone stream"
        )

    def _get_lan_url(self) -> str:
        try:
            with socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            ) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]

        except OSError:
            ip = "127.0.0.1"

        return f"https://{ip}:{self.config.get('port', 5000)}"

    def _refresh_url(self):
        self.url_var.set(self._get_lan_url())
        self.root.after(3000, self._refresh_url)

    def _copy_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_var.get())
        self.root.update()
        self.status_var.set("● URL copied to clipboard")
        self.root.after(1500, lambda: self.status_var.set("● Running"))

    def _open_config(self):
        import os, sys
        folder = app_dir()
        if sys.platform == "win32":
            os.startfile(folder.as_posix().replace("/", "\\"))
        else:
            os.system(f'xdg-open "{folder}"')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    defaults = load_json(resource_path("config/webconfig.json"))
    
    gui = SettingsWindow(defaults)
    gui.run()