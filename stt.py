import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import sys
import queue
import threading

SAMPLE_RATE = 16000
CHUNK_DURATION = 1
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

audio_queue = queue.Queue()
stop_event = threading.Event()
text_output = ""

def audioWorker():
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
            while not stop_event.is_set():
                audio_chunk, _ = stream.read(CHUNK_SIZE)
                if stop_event.is_set():
                    break
                flat_chunk = np.squeeze(audio_chunk)
                audio_queue.put(flat_chunk)
    except Exception as e:
        if not stop_event.is_set():
            print(f"\nAn error occurred: {e}")
            stop_event.set()

def main(model, MAX_SILENCE_CHUNKS=5):
    global text_output
    text_output = ""
    stop_event.clear()

    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            silence_count = 0
            break

    silence_count = 0
    
    audio_buffer = []

    recorder_thread = threading.Thread(target=audioWorker, daemon=True)
    recorder_thread.start()

    print("--> Start speaking, Ctrl-C to stop")

    try:
        while not stop_event.is_set():
            try:
                flat_chunk = audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            rms = np.sqrt(np.mean(flat_chunk**2))

            if rms < 0.007:
                silence_count += 1
                if silence_count > MAX_SILENCE_CHUNKS:
                    print("\n\nSilence detected. Ending STT")
                    break
            else:
                silence_count = 0

            audio_buffer.append(flat_chunk)
            full_audio_data = np.concatenate(audio_buffer)

            segments, _ = model.transcribe(full_audio_data, beam_size=2)
            text_output = "".join([segment.text for segment in segments])

            sys.stdout.write(f"\r{text_output}")
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nSTT ended")
        exitType = "manual"
    stop_event.set()
    recorder_thread.join(timeout=1.0)
    if silence_count <= 0:
        exitType = "timeout"
    else:
        exitType = "normal"
    return text_output, exitType
def loadModel():
    print("loading model...")
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    print("model loaded.")
    return model

if __name__ == "__main__":
    model = loadModel()
    text = main(model=model)
    print(text)