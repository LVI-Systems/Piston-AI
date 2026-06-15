print("Welcome to Piston AI!")
import stt
import piston
import tts
import asyncio
import sounddevice as sd
import normalize
import json
from pathlib import Path
import os

timeout = 3

def main():
    model = stt.loadModel()
    voice = tts.loadModel()
    pipeline = normalize.loadNormalizer()

    try:
        while True:
            while True:
                global timeout
                text, exitType = stt.main(model, timeout)
                if exitType == "timeout":
                    if not text.strip():
                        break
                elif exitType == "manual":
                    if not text.strip():
                        break
                    pass
                elif exitType == "normal":
                    exitType = ""
                if not text:
                    print("No text recognized")
                    break
                if not text.strip():
                    print("No text recognized.") 
                    break
                response, listen = piston.askPiston(text)
                if listen:
                    timeout = 3
                else:
                    timeout = 1
                asyncio.run(tts.speak(response, voice=voice))
                sd.stop()
                timeout = 3
    except KeyboardInterrupt:
        print("Goodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()