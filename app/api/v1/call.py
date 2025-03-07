from fastapi import APIRouter, status, Depends, HTTPException, WebSocket

from app.services.transcriber import DeepgramTranscriber
from app.core.logger import logger
from app.utils import send_message_to_socket


routes = APIRouter(prefix="/call", tags=["Call"])


@routes.websocket("/web_call")
async def web_call(websocket: WebSocket):
    await websocket.accept()
    deepgram_transcriber = DeepgramTranscriber(websocket)
    await deepgram_transcriber.start()
    await send_message_to_socket(websocket, "Hi there, How can i help you")
    try:
        while True:
            audio_data = await websocket.receive_bytes()
            await deepgram_transcriber.send(audio_data)
    except Exception as e:
        logger.error(f"Error occured in web call socket {e}")
        await deepgram_transcriber.stop()
