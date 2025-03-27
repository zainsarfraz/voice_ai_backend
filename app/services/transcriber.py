import json
import os
from random import randint

from fastapi import WebSocket
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

from app.services.chat_model import get_response
from app.utils import send_message_to_socket, send_message_to_twilio
from app.core.logger import logger
from app.models.assistant import Assistant


class DeepgramTranscriber:
    def __init__(
        self,
        client_socket: WebSocket,
        assistant: Assistant,
        call_type: str = "web",
        sid: str = "",
    ):
        self.client_socket = client_socket
        self.deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        self.dg_connection = self.deepgram.listen.asyncwebsocket.v("1")
        self.llm_chat_history_id = randint(0, 9999)
        self.assistant = assistant
        self.call_type = call_type
        self.sid = sid
        self._setup_event_handlers()

    async def send_first_message(self):
        if not self.assistant.first_message:
            first_message = "Hello"
        else:
            first_message = self.assistant.first_message

        if self.call_type == "twilio":
            await send_message_to_twilio(
                self.client_socket, first_message, self.assistant.voice, sid=self.sid
            )

        if self.call_type == "web":
            await send_message_to_socket(
                self.client_socket, first_message, self.assistant.voice
            )

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
        user_message = {"event": "message", "transcript": f"{sentence}"}
        await self.client_socket.send_text(json.dumps(user_message))
        response_text = get_response(self.assistant, self.llm_chat_history_id, sentence)

        if self.call_type == "twilio":
            await send_message_to_twilio(
                self.client_socket, response_text, self.assistant.voice, self.sid
            )
        if self.call_type == "web":
            await send_message_to_socket(
                self.client_socket, response_text, self.assistant.voice
            )

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
        if self.call_type == "web":
            return LiveOptions(model="nova-3", punctuate=True)
        if self.call_type == "twilio":
            return LiveOptions(
                model="nova-phonecall",
                language="en-US",
                channels=1,
                sample_rate=8000,
                encoding="mulaw",
                smart_format=True,
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
