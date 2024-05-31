from fastapi import FastAPI
from src.websockets.ws import ws
from src.endpoints.routes import endpoints

app = FastAPI()
app.mount("/ws", ws)

for endpoint in endpoints:
    app.include_router(endpoint.router)
