import os
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, Form, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Templates directory
templates = Jinja2Templates(directory="templates")

# FastAPI instance
app = FastAPI()

# Static files directories
app.mount("/static", StaticFiles(directory="templates"), name="static")

@app.get("/")
async def main_get(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "token": None})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
