import json
import base64

from fastapi import APIRouter, WebSocket
from twilio.rest import Client

from app.services.transcriber import DeepgramTranscriber
from app.core.logger import logger
from app.core.config import settings
from app.models.assistant import Assistant
from app.api.deps import SessionDep


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


@routes.post("/phone_call")
async def make_call(assistant_id: str, phone_number: str):
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    twiml = (
        f"""<Response>
                    <Connect>
                        <Stream url="wss://4d11-182-189-25-70.ngrok-free.app/api/v1/call/stream?assistant_id={assistant_id}"/>
                    </Connect>
                    <Pause length="60"/>
                </Response>""",
    )
    call = twilio_client.calls.create(
        twiml=twiml,
        to=phone_number,
        from_=settings.TWILIO_PHONE_NUMBER,
    )

    return {"message": "Call has been placed", "call_id": call.sid}


@routes.websocket("/stream")
async def stream_audio(websocket: WebSocket, session: SessionDep):
    """Handles WebSocket connections from Twilio Media Streams."""
    assistant = (
        session.query(Assistant)
        .filter(Assistant.id == "03a994cf-e09c-4a73-9cc2-6857c70a1ea3")
        .first()
    )

    logger.info("Connected to Twilio Media Stream")
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            event = message.get("event")

            if event == "start":
                streamSid = message["start"]["streamSid"]

                deepgram_transcriber = DeepgramTranscriber(
                    websocket, assistant, call_type="twilio", sid=streamSid
                )
                await deepgram_transcriber.start()
                await deepgram_transcriber.send_first_message()

            if event == "media":
                if message["media"]["track"] == "inbound":
                    payload_b64 = message["media"]["payload"]
                    payload = base64.b64decode(payload_b64)
                    if deepgram_transcriber:
                        await deepgram_transcriber.send(payload)

            elif event == "stop":
                await deepgram_transcriber.stop()

    except Exception as e:
        print("Error handling Twilio stream:", e)
