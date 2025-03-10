from fastapi import APIRouter, WebSocket

from app.services.transcriber import DeepgramTranscriber
from app.core.logger import logger
from app.utils import send_message_to_socket
from app.models.assistant import Assistant
from app.api.deps import CurrentUser, SessionDep, get_current_user


routes = APIRouter(prefix="/call", tags=["Call"])


@routes.websocket("/web_call")
async def web_call(websocket: WebSocket, assistant_id: str, session: SessionDep):
    
    assistant = session.query(Assistant).filter(Assistant.id == assistant_id).first()
    await websocket.accept()
    deepgram_transcriber = DeepgramTranscriber(websocket, assistant)
    await deepgram_transcriber.start()
    try:
        await deepgram_transcriber.send_first_message()
        while True:
            audio_data = await websocket.receive_bytes()
            await deepgram_transcriber.send(audio_data)
    except Exception as e:
        logger.error(f"Error occured in web call socket {e}")
        await deepgram_transcriber.stop()
