import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

ws = FastAPI()

ws.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@ws.websocket("/discussions")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
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