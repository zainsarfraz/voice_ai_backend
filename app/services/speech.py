import os
import requests


DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


async def get_speech(text: str):
    DEEPGRAM_SPEECH_API = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}
    tts_response = requests.post(DEEPGRAM_SPEECH_API, headers=headers, json=payload)

    return tts_response.content
