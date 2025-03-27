import os
import requests


DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


async def get_speech(text: str, voice: str, sid: str = ""):
    if sid:
        call_config = "&encoding=mulaw&sample_rate=8000&container=none"
    else:
        call_config = ""

    if voice.upper() == "MALE":
        voice = "aura-orion-en"
    elif voice.upper() == "FEMALE":
        voice = "aura-asteria-en"
    else:
        voice = "aura-orion-en"

    DEEPGRAM_SPEECH_API = (
        f"https://api.deepgram.com/v1/speak?model={voice}{call_config}"
    )
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}
    tts_response = requests.post(DEEPGRAM_SPEECH_API, headers=headers, json=payload)

    return tts_response.content
