from pathlib import Path
import sys
import json
import os 
import cv2
import threading
import numpy as np 
from flask import (
    Flask,
    request,
    Response,
    render_template_string,
    send_file
    )
import pyvirtualcam  
from folder import (
    load_json,
    load_config,
    save_config,
    app_dir,
    resource_path
)
import queue



INDEX_HTML = resource_path("html/website.html")
WEBCONFIG_PATH = resource_path("config/webconfig.json")
default_webconfig = load_json(WEBCONFIG_PATH)
CSS_FILE = resource_path("css/style.css")


_lock = threading.Lock()
_latest_frame = None
_audio_q = queue.Queue(maxsize=20)

app = Flask(__name__)

@app.route("/")
def index():
    return INDEX_HTML.read_text(encoding="utf-8")

@app.route("/css/style.css")
def css():
    return CSS_FILE.read_text(encoding="utf-8"), 200, {"Content-Type": "text/css"}


@app.route("/manifest.json")
def manifest():
    return send_file(
        resource_path("html/manifest.json"),
        mimetype="application/manifest+json"
    )


@app.route("/icons/icon192.png")
def icon192():
    return send_file(
        resource_path("icons/icon192.png"),
        mimetype="image/png"
    )


@app.route("/icons/icon512.png")
def icon512():
    return send_file(
        resource_path("icons/icon512.png"),
        mimetype="image/png"
    )

@app.route("/config/webconfig.json")
def webconfig():

    config = load_config(default_webconfig)

    return (
        json.dumps(config),
        200,
        {
            "Content-Type": "application/json",
            "Cache-Control": "no-store"
        }
    )


@app.route("/frame", methods=["POST"])
def frame():

    global _latest_frame

    raw = request.get_data()

    if not raw:
        return "Empty frame", 400

    arr = np.frombuffer(raw, dtype=np.uint8)

    try:
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except cv2.error:
        return "Invalid JPEG", 400

    if img is None:
        return "Invalid JPEG", 400

    with _lock:
        _latest_frame = img

    return "", 204

@app.route("/audio", methods=["POST"])
def audio():

    raw = request.get_data()

    if not raw or len(raw) % 2 != 0:
        return "Invalid audio data", 400

    samples = np.frombuffer(raw, dtype="<i2")

    try:
        _audio_q.put_nowait(samples)

    except queue.Full:
        pass

    return "", 204

def audio_debug():
    """Temporary: proves audio data is reaching the PC."""
    total = 0
    while True:
        chunk = _audio_q.get()
        total += len(chunk)
        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
        print(f"audio chunk: {len(chunk)} samples, RMS={rms:.0f}, total={total}")

def webcam_loop(gui):

    cam = None
    current_key = None

    try:
        while True:

            cfg = gui.config

            width = cfg["width"]
            height = cfg["height"]
            fps = cfg["fps"]

            key = (width, height, fps)

            # Recreate webcam when settings change
            if key != current_key:

                if cam is not None:
                    cam.close()
                    cam = None

                cam = pyvirtualcam.Camera(
                    width=width,
                    height=height,
                    fps=fps
                )
                print("Camera device:", cam.device)
                print("Camera backend:", cam.backend)
                current_key = key

                print(
                    f"Virtual camera: "
                    f"{width}x{height} @ {fps} FPS"
                )

            # Read the latest available frame
            with _lock:
                frame = _latest_frame

            if frame is None:

                # Black frame before phone connects
                rgb = np.zeros(
                    (height, width, 3),
                    dtype=np.uint8
                )

            else:

                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(
                        frame,
                        (width, height)
                    )

                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

            cam.send(rgb)
            cam.sleep_until_next_frame()

    finally:

        if cam is not None:
            cam.close()

def run_flask(port):

    
    app.run(
        host="0.0.0.0",
        port=port,
        use_reloader=False,
        threaded=True,
    )
