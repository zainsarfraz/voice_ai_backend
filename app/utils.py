import base64
import json

from fastapi import WebSocket

from app.core import security
from app.models.user import User
from app.schemas.common import Token
from app.services.speech import get_speech


def generate_token_response_data(user: User) -> Token:
    extra_data = {"email": user.email}

    return Token(
        access_token=security.create_jwt_token(subject=user.id, extra_data=extra_data),
        refresh_token=security.create_jwt_token(
            subject=user.id, extra_data=extra_data, refresh=True
        ),
    )


async def send_message_to_socket(websocket: WebSocket, message: str):
    speech = await get_speech(message)
    media_message = {
        "event": "media",
        "transcript": f"{message}",
        "streamSid": "",
        "media": {
            "payload": base64.b64encode(speech).decode("ascii"),
            "track": "outbound",
        },
    }
    await websocket.send_text(json.dumps(media_message))
