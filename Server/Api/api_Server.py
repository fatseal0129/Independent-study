# 與BOX的websocket連接 Client端使用websocket-client
import base64
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from websockets.exceptions import ConnectionClosed
import uvicorn
from Server.Service import DetectManager, FileManager, DB
from model import CameraInfo, MemberInfo
from typing import Annotated

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
    if DB.addCamera(cam_info.name, cam_info.mode, cam_info.url, cam_info.state):
        DetectManager.addDetectCam(cam_info.name, cam_info.mode, cam_info.state)

# 取得攝影機mode, name資料
@app.get('/server/camera/modeinfo')
async def getCameraInfo():
    cam = DB.getAllCamName_with_Mode()
    return cam

# 取得攝影機state, name資料
@app.get('/server/camera/stateinfo')
async def getCameraModeNState():
    states = DB.getAllCamName_with_State()
    return states

# 設置攝影機模式
@app.get('/server/camera/setmode/{mode}')
async def setCameraMode(mode: str):
    pass

# 編輯成員
@app.put('/member/edit/{oldname}')
async def editMember(oldname: str, new_member: MemberInfo):
    new_image = base64.b64decode(new_member.image)
    new_avatar = base64.b64decode(new_member.avatar)

    oldimgpath = DB.getMemberImagePath(oldname)
    oldimgfilename = DB.getMemberImageFileName(oldname)

    oldavatarpath = DB.getMemberAvatarPath(oldname)
    oldavatarfilename = DB.getMemberAvatarFileName(oldname)

    if FileManager.DeleteImage(path=oldimgpath, filename=oldimgfilename) and \
            FileManager.DeleteImage(path=oldavatarpath, filename=oldavatarfilename) and DB.DeleteMember(oldname):
        try:
            imageFileName, imagePath, avatarFileName, avatarPath = FileManager.saveImage(new_image, new_avatar, new_member.name)
        except Exception as e:
            return {"message": f'寫入檔案失敗, 原因：{e}'}
        if DB.addMemberToDatabase(name=new_member.name, imgfilename=imageFileName, avatarFileName=avatarFileName,
                                  avatarpath=avatarPath, imagepath=imagePath):
            DetectManager.reflashingDetectData()
            return {"message": "success!"}
        return {"message": "寫入資料庫失敗！"}
    else:
        return {"message": "刪除失敗！原因：查無資料"}


# 刪除人員
@app.delete('/member/delete/{name}')
async def deleteMember(name: str):
    pass

# 新增人員
@app.post('/member/add')
async def addMember(member: MemberInfo):
    image = base64.b64decode(member.image)
    avatar = base64.b64decode(member.avatar)

    # 先儲存檔案成功再寫入資料庫
    try:
        imageFileName, imagePath, avatarFileName, avatarPath = FileManager.saveImage(image, avatar, member.name)
    except Exception as e:
        return {"message": f'寫入檔案失敗, 原因：{e}'}
    if DB.addMemberToDatabase(name=member.name, imgfilename=imageFileName, avatarFileName=avatarFileName,
                              avatarpath=avatarPath, imagepath=imagePath):
        DetectManager.reflashingDetectData()
        return {"message": "success!"}
    return {"message": "寫入資料庫失敗"}

# 取得所有人員(包含檢查成員)
@app.get('/member/getAll')
async def getAllMember():
    allMember = []
    temp_avatar_list = list()

    avatarpath = DB.getAllMemberAvatarPath()
    avatarfilename = DB.getAllMemberAvatarFileNames()
    names = DB.getAllMemberNames()
    if len(names) == 0:
        return {'name': 'NoMemberHasAdded', 'avatar': 'NoMemberHasAdded'}
    try:
        temp_avatar_list = FileManager.loadingKnowAvatar(nameList=avatarfilename, pathList=avatarpath)
    except FileNotFoundError as e:
        print(f'取得temp_avatar_list失敗! 原因：{e}')
        return {"name": "FileNotFoundError", "avatar": "FileNotFoundError"}
    for pic, name in zip(temp_avatar_list, names):
        encode_pic = base64.b64encode(pic)
        allMember.append({
            "name": name,
            "avatar": encode_pic
        })
    return allMember

# 取得單個可疑人士影片
@app.get('/sus/get/video/{videopath}')
async def getSUSVideo(videopath: Annotated[str, Path(title="影片路徑")]):
    paths = DB.getAllSUSVideoPath()
    if videopath in paths:
        return FileResponse(videopath)
    else:
        return {"message": "FileNotFound!"}

# 取得單個可疑人士照片
@app.get('/sus/get/video/{imagepath}')
async def getSUSImage(imagepath: Annotated[str, Path(title="照片路徑")]):
    paths = DB.getAllSUSImagePath()
    if imagepath in paths:
        return FileResponse(imagepath)
    else:
        return {"message": "FileNotFound!"}

# 取得全部可疑人士資訊
@app.get('/sus/get/all')
async def getALLSUSMember():
    allSUS = []
    temp_sus_list = DB.getAllSUS()

    for imposter in temp_sus_list:
        videopath = os.path.join(imposter['videoPath'], imposter['vidFilename'])
        imagepath = os.path.join(imposter['imagePath'], imposter['imgFilename'])
        sus = {
            "appear_time": imposter['appear'],
            "videopath": videopath,
            "imagepath": imagepath
        }
        allSUS.append(sus)
    return allSUS

@app.websocket("/ws")
async def read_webscoket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            raw_time = await websocket.receive_text()
            if raw_data == "{}":
                continue
            else:
                data = eval(raw_data)
                current_time = eval(raw_time)
                DetectManager.Detect(data, current_time)
    except WebSocketDisconnect:
        print("Box Disconnected! reason: 'WebSocketDisconnect'")
    except ConnectionClosed:
        print("Box Disconnected! reason: 'ConnectionClosed'")


if __name__ == "__main__":
    uvicorn.run("api_Server:app", reload=True)
