import sounddevice as sd
import queue
import json
import numpy as np
from vosk import Model, KaldiRecognizer

# 1) Path to the *English* Vosk model:
MODEL_PATH = "/home/luisvinatea/Dev/Repos/genealogy/tools/vosk-model-small-en-us-0.15"  # Update path

# If your monitor device doesn't support 16k natively,
# we'll open it at 48k and resample in software.
INPUT_SR = 48000  # typical sampling rate for many monitor devices
TARGET_SR = 16000  # Vosk model's preferred rate

# 2) Device index or name (assuming same monitor):
MONITOR_DEVICE = 7  # or whatever matches your system

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, TARGET_SR)
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    # 'indata' is raw bytes (int16) at INPUT_SR sample rate
    audio_queue.put(bytes(indata))

def main():
    # We open the stream at 48k
    # Then do software resampling to 16k
    with sd.RawInputStream(
        samplerate=INPUT_SR,
        blocksize=24000,  # ~0.5 sec of audio at 48k
        device=MONITOR_DEVICE,
        dtype='int16',
        channels=1,
        callback=audio_callback,
    ):
        print("English transcription running. Press Ctrl+C to stop.")

        # We'll do an on-the-fly resampling using the 'resampy' library
        import resampy

        while True:
            data = audio_queue.get()

            # Convert raw bytes -> numpy array of shape [N,], dtype int16
            samples_48k = np.frombuffer(data, dtype=np.int16)

            # Resample from 48k to 16k (float -> float)
            samples_16k = resampy.resample(
                samples_48k.astype(np.float32),
                INPUT_SR,
                TARGET_SR
            )

            # Convert back to int16 bytes for Vosk
            resampled_bytes = samples_16k.astype(np.int16).tobytes()

            if recognizer.AcceptWaveform(resampled_bytes):
                # Full utterance recognized
                result_json = recognizer.Result()
                result_dict = json.loads(result_json)
                text = result_dict.get("text", "")
                if text.strip():
                    print(f"\n[English - Complete Text] {text}")
                    with open("english_transcript.log", "a") as f:
                        f.write(text + "\n")
            else:
                # Partial recognition
                partial_json = recognizer.PartialResult()
                partial_dict = json.loads(partial_json)
                partial_text = partial_dict.get("partial", "")
                print(f"\r[English - Partial] {partial_text}", end='', flush=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting english transcription...")
