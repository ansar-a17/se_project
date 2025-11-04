import threading
from pynput import keyboard
import mss
from PIL import Image
from image_to_text import image_to_text
from text_to_speech import text_to_speech

HOTKEY = '<f9>'

def process_image(img: Image.Image):
    print("Captured image size:", img.size)
    text = image_to_text(img)
    text_to_speech(text)

def take_screenshot():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        process_image(img)
    except Exception as e:
        print("Error taking screenshot:", e)


def on_activate_screenshot():
    threading.Thread(target=take_screenshot, daemon=True).start()


def main():
    print(f"Listening for {HOTKEY}... (press Ctrl+C in the console to quit)")
    with keyboard.GlobalHotKeys({HOTKEY: on_activate_screenshot}) as h:
        h.join()


if __name__ == '__main__':
    main()
