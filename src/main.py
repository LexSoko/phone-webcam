from server import run_flask, webcam_loop, audio_debug
from gui import SettingsWindow
from folder import load_json, resource_path
import threading


if __name__ == "__main__":

    defaults = load_json(
        resource_path("config/webconfig.json")
    )

    gui = SettingsWindow(defaults)

    # Flask server thread
    threading.Thread(
        target=run_flask,
        args=(gui.config["port"],),
        daemon=True
    ).start()

    # Virtual webcam thread
    threading.Thread(
        target=webcam_loop,
        args=(gui,),
        daemon=True
    ).start()

    # Temporary audio debugging thread
    threading.Thread(
        target=audio_debug,
        daemon=True
    ).start()

    # Main GUI thread
    gui.run()