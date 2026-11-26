"""
Runs on PC. Serves the capture page to the phone, receives JPEG frames,
and pushes them to a virtual webcam.
"""
import threading
import cv2
import numpy as np
from flask import Flask, request, Response, render_template_string

import pyvirtualcam

app = Flask(__name__)

# Shared latest frame (single writer, single reader -> lock is cheap)
_lock = threading.Lock()
_latest_frame = None          # BGR ndarray
_frame_event = threading.Event()

PAGE = """
<!doctype html>
<html>
<body style="background:#111;color:#eee;font-family:sans-serif;text-align:center">
<h3>Phone Webcam</h3>
<video id="v" autoplay playsinline muted width="320"></video><br>
<canvas id="c" hidden></canvas>
<button onclick="start()" style="font-size:1.2em;padding:.6em 1.2em">Start Streaming</button>
<p id="status">idle</p>
<script>
let video = document.getElementById('v');
let canvas = document.getElementById('c');
let ctx = canvas.getContext('2d');
let sending = false;

async function start() {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: 'environment', width: {ideal: 1280}, height: {ideal: 720} },
    audio: false
  });
  video.srcObject = stream;
  await video.play();
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  sending = true;
  document.getElementById('status').textContent = 'streaming...';
  sendLoop();
}

async function sendLoop() {
  if (!sending) return;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(async (blob) => {
    try {
      await fetch('/frame', { method: 'POST', body: blob });
    } catch(e) { console.error(e); }
    setTimeout(sendLoop, 66);   // ~15 fps
  }, 'image/jpeg', 0.7);
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/frame", methods=["POST"])
def frame():
    global _latest_frame
    data = np.frombuffer(request.get_data(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is not None:
        with _lock:
            _latest_frame = img
        _frame_event.set()
    return "", 204


def webcam_loop(width=1280, height=720, fps=15):
    with pyvirtualcam.Camera(width=width, height=height, fps=fps) as cam:
        print(f"Virtual camera device: {cam.device}")
        while True:
            _frame_event.wait(timeout=1.0)
            _frame_event.clear()
            with _lock:
                frame = _latest_frame
            if frame is None:
                continue
            frame = cv2.resize(frame, (width, height))
            cam.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


if __name__ == "__main__":
    t = threading.Thread(target=webcam_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)