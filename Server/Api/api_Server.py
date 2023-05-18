# 與BOX的websocket連接 Client端使用websocket-client

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import Detect.DetectService


class CameraInfo(BaseModel):
    name: str
    mode: str
    state: bool


detectManager = Detect.DetectService.DetectManager()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/server/add/Detect')
async def addDetect(cam_info: CameraInfo):
    detectManager.addDetectCam(cam_info.name, cam_info.mode, cam_info.state)


@app.websocket("/ws")
async def read_webscoket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            raw_time = await websocket.receive_text()
            if raw_data == "":
                continue
            else:
                data = eval(raw_data)
                current_time = eval(raw_time)
                detectManager.Detect(data, current_time)
    except WebSocketDisconnect:
        print("Box Disconnected! reason: 'WebSocketDisconnect'")
    except ConnectionClosed:
        print("Box Disconnected! reason: 'ConnectionClosed'")


if __name__ == "__main__":
    uvicorn.run("api_Server:app", reload=True)
