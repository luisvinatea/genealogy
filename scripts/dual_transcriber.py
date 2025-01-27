import sounddevice as sd
import queue
import json
import numpy as np
from vosk import Model, KaldiRecognizer
import resampy

# Adjust these paths to your models:
ENGLISH_MODEL_PATH = (
    "/home/luisvinatea/Dev/Repos/genealogy/tools/vosk-model-small-en-us-0.15"
)
SPANISH_MODEL_PATH = (
    "/home/luisvinatea/Dev/Repos/genealogy/tools/vosk-model-small-es-0.42"
)

# If your monitor device doesn't support 16k natively,
# open it at 48k and resample down to 16k.
INPUT_SR = 48000   # typical sampling rate for many monitor devices
TARGET_SR = 16000  # Vosk model's preferred rate

# Use the same monitor device index or name for both
MONITOR_DEVICE = 2  # or device name string

# 1) Load each model
english_model = Model(ENGLISH_MODEL_PATH)
spanish_model = Model(SPANISH_MODEL_PATH)

# 2) Create a recognizer for each model
english_recognizer = KaldiRecognizer(english_model, TARGET_SR)
spanish_recognizer = KaldiRecognizer(spanish_model, TARGET_SR)

audio_queue = queue.Queue()

# ANSI color codes for simple flag-like coloring:
RESET = "\033[0m"
# Spanish: red background + bright yellow text
SPANISH_COLOR = "\033[101m\033[93m"  # bright red BG, bright yellow FG
# English: blue background + bright white text
ENGLISH_COLOR = "\033[104m\033[97m"  # bright blue BG, bright white FG


def audio_callback(indata, frames, time, status):
    """Sounddevice callback: push raw bytes into a queue."""
    if status:
        print(status, flush=True)
    audio_queue.put(bytes(indata))


def main():
    print("Starting dual English/Spanish transcription. Press Ctrl+C to stop.")

    # Open the monitor device once, at 48k
    with sd.RawInputStream(
        samplerate=INPUT_SR,
        blocksize=24000,  # about 0.5 seconds at 48k
        device=MONITOR_DEVICE,
        dtype='int16',
        channels=1,
        callback=audio_callback,
    ):
        while True:
            data = audio_queue.get()

            # Convert raw bytes to a NumPy array
            samples_48k = np.frombuffer(data, dtype=np.int16)
            samples_48k = samples_48k.astype(np.float32)

            # Resample from 48k -> 16k
            samples_16k = resampy.resample(samples_48k, INPUT_SR, TARGET_SR)

            # Convert back to int16 for Vosk
            resampled_bytes = samples_16k.astype(np.int16).tobytes()

            #
            # ---- FEED to ENGLISH recognizer ----
            #
            # ...
            if english_recognizer.AcceptWaveform(resampled_bytes):
                # Full English
                eng_result_json = english_recognizer.Result()
                eng_result_dict = json.loads(eng_result_json)
                eng_text = eng_result_dict.get("text", "").strip()
                if eng_text:
                    # Print final English result in color, with US flag
                    colored_eng = f"{ENGLISH_COLOR}[🇺🇸 EN] {eng_text}{RESET}"
                    print(f"\n{colored_eng}")
                    # Write plain text to log
                    with open("english_transcript.log", "a") as f:
                        f.write(eng_text + "\n")
            else:
                # No partial printing (less clutter)
                pass

            #
            # ---- FEED to SPANISH recognizer ----
            #
            if spanish_recognizer.AcceptWaveform(resampled_bytes):
                # We got a final Spanish utterance
                es_result_json = spanish_recognizer.Result()
                es_result_dict = json.loads(es_result_json)
                es_text = es_result_dict.get("text", "").strip()
                if es_text:
                    # Print final Spanish result in color, with Spain flag
                    colored_es = f"{SPANISH_COLOR}[🇪🇸 ES] {es_text}{RESET}"
                    print(f"\n{colored_es}")
                    # Write plain text to log
                    with open("spanish_transcript.log", "a") as f:
                        f.write(es_text + "\n")
            else:
                # No partial printing (less clutter)
                pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting dual-language transcription.")
