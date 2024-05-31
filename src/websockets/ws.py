import json
import uuid
from fastapi import Depends, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from src.models.message import Message
from src.services.message import MessageService

ws = FastAPI()

ws.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@ws.websocket("/discussions")
async def websocket_endpoint(
    websocket: WebSocket,
    message_service: MessageService = Depends(MessageService),
):
    await websocket.accept()
    while True:
        data = json.loads(await websocket.receive_text())

        user_message = Message.create(
            role="user",
            message=data["message"],
            discussion_id=uuid.UUID(data["discussion_id"]).bytes,
        )

        await message_service.create_message(
            message=user_message,
        )

        await websocket.send_text(
            json.dumps(
                {
                    "message": f"You wrote: {data}",
                    "role": "bot",
                }
            )
        )

        await websocket.send_text(
            json.dumps(
                {
                    "message": "3회 남았습니다.",
                    "role": "system",
                }
            )
        )
