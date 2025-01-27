import sounddevice as sd
import queue
import json
import numpy as np
from vosk import Model, KaldiRecognizer
import resampy
import os

# Adjust these paths to your models:
ENGLISH_MODEL_PATH = "/home/luisvinatea/Dev/Repos/genealogy/tools/vosk-model-small-en-us-0.15"
SPANISH_MODEL_PATH = "/home/luisvinatea/Dev/Repos/genealogy/tools/vosk-model-small-es-0.42"

# Output directories for transcriptions
ENGLISH_OUTPUT_DIR = "/home/luisvinatea/Dev/Repos/genealogy/data/vosk_model/raw_transcripts/en"
SPANISH_OUTPUT_DIR = "/home/luisvinatea/Dev/Repos/genealogy/data/vosk_model/raw_transcripts/es"

# If your monitor device doesn't support 16k natively,
# open it at 48k and resample down to 16k.
INPUT_SR = 48000   # typical sampling rate for many monitor devices
TARGET_SR = 16000  # Vosk model's preferred rate

# Use the same monitor device index or name for both
MONITOR_DEVICE = MONITOR_DEVICE = "Family 17h/19h/1ah HD Audio Controller Analog Stereo, JACK Audio Connection Kit"  # or device name string

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

def ensure_directory_exists(directory):
    """Ensure that the specified directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_new_file_path(directory, language):
    """Generate a new file path with incrementing numbers."""
    ensure_directory_exists(directory)
    existing_files = [f for f in os.listdir(directory) if f.startswith(language) and f.endswith(".txt")]
    numbers = [int(f.split("_")[1].split(".")[0]) for f in existing_files if "_" in f and f.split("_")[1].isdigit()]
    next_number = max(numbers) + 1 if numbers else 1
    return os.path.join(directory, f"{language}_{next_number}.txt")

def audio_callback(indata, frames, time, status):
    """Sounddevice callback: push raw bytes into a queue."""
    if status:
        print(status, flush=True)
    audio_queue.put(bytes(indata))

def main():
    print("Starting dual English/Spanish transcription. Press Ctrl+C to stop.")

    # Initialize output file paths
    english_file_path = get_new_file_path(ENGLISH_OUTPUT_DIR, "english")
    spanish_file_path = get_new_file_path(SPANISH_OUTPUT_DIR, "spanish")

    english_lines = []
    spanish_lines = []

    # Open the monitor device once, at 48k
    with sd.RawInputStream(
        samplerate=INPUT_SR,
        blocksize=24000,  # about 0.5 seconds at 48k
        device=MONITOR_DEVICE,
        dtype='int16',
        channels=1,
        callback=audio_callback,
    ):
        try:
            while True:
                data = audio_queue.get()

                # Convert raw bytes to a NumPy array
                samples_48k = np.frombuffer(data, dtype=np.int16)
                samples_48k = samples_48k.astype(np.float32)

                # Resample from 48k -> 16k
                samples_16k = resampy.resample(samples_48k, INPUT_SR, TARGET_SR)

                # Convert back to int16 for Vosk
                resampled_bytes = samples_16k.astype(np.int16).tobytes()

                # Process English transcription
                if english_recognizer.AcceptWaveform(resampled_bytes):
                    eng_result_json = english_recognizer.Result()
                    eng_result_dict = json.loads(eng_result_json)
                    eng_text = eng_result_dict.get("text", "").strip()
                    if eng_text:
                        english_lines.append(eng_text)
                        colored_eng = f"{ENGLISH_COLOR}[EN] {eng_text}{RESET}"
                        print(f"\n{colored_eng}")

                # Process Spanish transcription
                if spanish_recognizer.AcceptWaveform(resampled_bytes):
                    es_result_json = spanish_recognizer.Result()
                    es_result_dict = json.loads(es_result_json)
                    es_text = es_result_dict.get("text", "").strip()
                    if es_text:
                        spanish_lines.append(es_text)
                        colored_es = f"{SPANISH_COLOR}[ES] {es_text}{RESET}"
                        print(f"\n{colored_es}")
        except KeyboardInterrupt:
            print("\nFinalizing transcriptions...")

            # Write English lines to file
            with open(english_file_path, "w") as f:
                f.write("\n".join(english_lines))

            # Write Spanish lines to file
            with open(spanish_file_path, "w") as f:
                f.write("\n".join(spanish_lines))

            print(f"English transcription saved to: {english_file_path}")
            print(f"Spanish transcription saved to: {spanish_file_path}")

if __name__ == "__main__":
    main()
