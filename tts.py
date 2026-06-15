import numpy as np
import sounddevice as sd
from piper import PiperVoice, SynthesisConfig
import asyncio
from pathlib import Path
import urllib.request

def loadModel(path="data/kusal.onnx"):
    print("Loading voice...")
    voice = PiperVoice.load(path)
    return voice

async def speak(text:str="", path="data/kusal.onnx", voice:str=None):
    if voice is None:
        return
    try:
        if not text.strip():
            return
        synConfig = SynthesisConfig(
            volume=0.9,
            length_scale=1.0
        )

        sampleRate = voice.config.sample_rate

        with sd.RawOutputStream(samplerate=sampleRate, channels=1, dtype='int16') as stream:
            stream.start()

            for chunk in voice.synthesize(text, syn_config=synConfig):
                stream.write(chunk.audio_int16_bytes)
            
            stream.stop()
    except Exception as e:
        print(f"Error synthesizing: {e}")
    
def downloadVoice(output:str="data/", voice="kusal", quality:str="medium"):
    try:
        print("Downloading TTS model...")

        downloadPath = Path(output)
        downloadPath.mkdir(parents=True, exist_ok=True)

        onnxFile = downloadPath / f"{voice}.onnx"
        jsonFile = downloadPath / f"{voice}.onnx.json"

        if Path(onnxFile).exists() and Path(jsonFile).exists():
            return 
        downloadURL = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/{voice}/{quality}/en_US-{voice}-{quality}.onnx?download=true"
        urllib.request.urlretrieve(downloadURL, onnxFile)
        jsonURL = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/{voice}/{quality}/en_US-{voice}-{quality}.onnx.json?download=true"
        urllib.request.urlretrieve(jsonURL, jsonFile)
        print("Model downloaded successfully!")
        return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

if __name__ == "__main__":
    downloadVoice()
    asyncio.run(speak("This is a test.", voice=loadModel))