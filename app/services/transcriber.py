import json
import os
import base64
from random import randint

from fastapi import WebSocket
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

from app.services.chat_model import get_response
from app.services.speech import get_speech
from app.utils import send_message_to_socket
from app.core.logger import logger


class DeepgramTranscriber:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        self.dg_connection = self.deepgram.listen.asyncwebsocket.v("1")
        self.llm_chat_history_id = randint(0, 9999)
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        event_handlers = {
            LiveTranscriptionEvents.Open: self._on_open,
            LiveTranscriptionEvents.Transcript: self._on_transcript,
            LiveTranscriptionEvents.SpeechStarted: self._on_speech_started,
            LiveTranscriptionEvents.UtteranceEnd: self._on_utterance_end,
            LiveTranscriptionEvents.Close: self._on_close,
            LiveTranscriptionEvents.Error: self._on_error,
            LiveTranscriptionEvents.Unhandled: self._on_unhandled,
        }
        for event, handler in event_handlers.items():
            self.dg_connection.on(event, handler)
    
    async def _on_open(self, *_):
        pass
    
    async def _on_transcript(self, _, result, **__):
        sentence = result.channel.alternatives[0].transcript
        if not sentence:
            return
        user_message = {
            "event": "message",
            "transcript": f"{sentence}"
        }
        await self.client_socket.send_text(json.dumps(user_message))
        response_text = get_response(self.llm_chat_history_id, sentence)
        await send_message_to_socket(self.client_socket, response_text)
    
    
    async def _on_speech_started(self, _, event, **__):
        pass
    
    async def _on_utterance_end(self, _, event, **__):
        pass
    
    async def _on_close(self, *_):
        pass
    
    async def _on_error(self, _, error, **__):
        pass
    
    async def _on_unhandled(self, _, event, **__):
        pass
    
    def _get_live_options(self) -> LiveOptions:
        return LiveOptions(
            model="nova-3"
        )
    
    async def start(self):
        if await self.dg_connection.start(self._get_live_options()) is False:
            logger.error("Deepgram connection failed.")
            return None
        return self.dg_connection
    
    async def stop(self):
        await self.dg_connection.finish()

    async def send(self, payload):
        await self.dg_connection.send(payload)