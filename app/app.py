from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
import time
import asyncio
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    G = [99.9497337, 96.44587571, 97.78343486, 96.28324787, 96.15114453, 96.70875337, 87.93178639, 76.15651759,
         59.93505872, 41.84069101]
    shear_strain = [8.36201169e-07, 1.83437208e-06, 4.11686470e-06, 8.95700624e-06, 1.98529674e-05, 4.39205547e-05,
                    9.62087004e-05, 2.14844133e-04, 4.72252237e-04, 1.03690620e-03]
    try:
        while True:
            for i in range(len(shear_strain)):
                data = {"timestamp": shear_strain[i], "value": G[i]}
                await websocket.send_json(data)
                await asyncio.sleep(3)
            raise WebSocketDisconnect
    except WebSocketDisconnect:
        print("Client disconnected")