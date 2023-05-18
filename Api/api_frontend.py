import threading
import base64
import time
from models import Cameta_info
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from fastapi.responses import StreamingResponse
from websockets.exceptions import ConnectionClosed
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Service import CameraManager, ServerManager, FileService
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 新增攝影機
@app.post('/camera/add')
async def createCamera(info: Cameta_info):
    print(info.url)
    result = CameraManager.createCamera(url=0, name=info.name, initial_mode=info.init_mode)
    # 若 result = TRUE 就呼叫sendServer來建立Detect服務
    if result:
        ServerManager.createConnect_to_Server(info.name, info.init_mode, True)

# 刪除攝影機
@app.delete('/camera/delete')
async def DeleteCamera(name: str):
    result = CameraManager.cleanCamera(name)
    if result:
        return {"message": "Success!"}
    else:
        return {"message": "Fail!"}

# 拿取全部可疑人士
@app.get('/sus/get/all')
async def getALLSUSMember():
    pass

# 顯示成員
@app.get('/member/get')
async def getAllMember():
    allMember = []
    avatarList, nameList = FileService.loadingKnowAvatar()
    for avatar, name in zip(avatarList, nameList):
        encode = base64.b64encode(avatar)
        allMember.append({
            "Name": name,
            "Avatar": encode
        })
    return allMember


# 新增成員
@app.post("/member/add")
async def addMember(response):
    image = base64.b64decode(response['Image'])
    avatar = base64.b64decode(response['Avatar'])
    name = response['Name']
    if FileService.saveImage(image, name, avatar):
        return {"message": "success!"}
    else:
        return {"message": "Fail!"}

# 編輯成員
@app.post('/member/edit')
async def editMember(response):
    pass

# 檢查成員

if __name__ == "__main__":
    uvicorn.run("api:app", reload=True)


