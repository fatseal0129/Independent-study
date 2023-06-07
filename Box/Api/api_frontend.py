import base64
# import time
from Box.Api.models import Camera_info, Camera_change_mode
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Box.Service import CamService
# from typing import Annotated
import Box.Service.SendServerService as sendService
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 創建Manager
camManager = CamService.CameraManager()
serverManager = sendService.sendService()

# 新增攝影機
@app.post('/camera/add')
async def createCamera(info: Camera_info):
    # 這之後要改一下
    try:
        # 新增攝影機
        # camManager.createCamera(url=0, name=info.name, initial_mode=info.init_mode)
        pass
    except KeyError:
        return {"message": "名字已存在！"}
    except Exception as e:
        return {"message": f'不知名錯誤, 原因:{e}'}
    # 與伺服器建立連線
    try:
        serverManager.createConnect_to_Server(name=info.name, mode=info.init_mode, state=False, url=info.url)
    except Exception as e:
        return {"message": f'{e}'}
    return {"message": f'success'}

# 取得攝影機截圖
@app.get('/camera/screenshot/{name}')
async def cameraResume(name: str):
    try:
        frame = camManager.getScreenShot(name)
    except Exception as e:
        return {"message": f'不知名錯誤, 原因:{e}'}
    return {"message": frame}

# 更換攝影機模式
@app.post('/camera/changemode')
async def changeCameraMode(info: Camera_change_mode):
    try:
        # serverManager.changeCameraResume(name)
        serverManager.changeCameraMode(info.name, info.mode)
    except Exception as e:
        return {"message": f'不知名錯誤, 原因:{e}'}
    return {"message": f'success'}

# 開始攝影機
@app.get('/camera/status/resume/{name}')
async def cameraResume(name: str):
    try:
        serverManager.changeCameraResume(name)
    except Exception as e:
        return {"message": f'不知名錯誤, 原因:{e}'}
    return {"message": f'success'}

# 暫停攝影機
@app.get('/camera/status/paused/{name}')
async def cameraPaused(name: str):
    try:
        serverManager.changeCameraPaused(name)
    except Exception as e:
        return {"message": f'不知名錯誤, 原因:{e}'}
    return {"message": f'success'}

# 刪除攝影機
@app.delete('/camera/delete/{name}')
async def DeleteCamera(name: str):
    try:
        camManager.cleanCamera(name)
        serverManager.cleanConnection(name)
    except Exception as e:
        return {"message": f'刪除失敗！ 原因:{e}'}
    return {"message": f'success'}

if __name__ == "__main__":
    uvicorn.run("api:app", reload=True)


