import base64
# import time
from models import Cameta_info
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Box.Service import CamService
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
async def createCamera(info: Cameta_info):
    print(info.url)
    try:
        camManager.createCamera(url=0, name=info.name, initial_mode=info.init_mode)
    # 若 result = TRUE 就呼叫sendServer來建立Detect服務
    except KeyError:
        return {"message": "名字已存在！"}
    except Exception as e:
        return {"message": f'不知名錯誤, 原因{e}'}

    serverManager.createConnect_to_Server(name=info.name, mode=info.init_mode, state=True, url=info.url)

# 刪除攝影機
@app.delete('/camera/delete')
async def DeleteCamera(name: str):

    ## 要實作資料庫要刪除攝影機
    result = camManager.cleanCamera(name)
    if result:
        return {"message": "Success!"}
    else:
        return {"message": "Fail!"}

# 更改攝影機模式

if __name__ == "__main__":
    uvicorn.run("api:app", reload=True)


