import queue
import numpy as np
import wave
import time

from server import _audio_q


def audio_debug():
    """Temporary: proves audio data is reaching the PC."""
    total = 0
    while True:
        chunk = _audio_q.get()
        total += len(chunk)
        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
        print(f"audio chunk: {len(chunk)} samples, RMS={rms:.0f}, total={total}")


def dump_wav(path="test.wav", seconds=3, rate=16000):
    chunks = []
    end = time.time() + seconds
    while time.time() < end:
        try:
            chunks.append(_audio_q.get(timeout=0.5))
        except queue.Empty:
            pass
    data = np.concatenate(chunks) if chunks else np.zeros(1, np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())
    print("wrote", path)