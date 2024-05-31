import os

import uvicorn
from fastapi import FastAPI, Form, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.websockets.ws import ws
from src.endpoints.routes import endpoints

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/ws", ws)

for endpoint in endpoints:
    app.include_router(endpoint.router)

app.mount("/static", StaticFiles(directory="templates"), name="static")

@app.get("/")
async def main_get(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "token": None})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)