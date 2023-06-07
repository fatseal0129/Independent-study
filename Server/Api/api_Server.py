# 與BOX的websocket連接 Client端使用websocket-client
import base64
import asyncio
import datetime
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from websockets.exceptions import ConnectionClosed
import uvicorn
from Server.Service import DetectManager, FileManager, DB
from Server.Api.model import CameraInfo, MemberInfo, CameraStateInfo, CameraModeInfo
from typing import Annotated
import cv2

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
async def getCameraMode():
    cam = DB.getAllCamName_with_Mode()
    return cam

# 取得攝影機state, name資料
@app.get('/server/camera/stateinfo')
async def getCameraState():
    states = DB.getAllCamName_with_State()
    return states


# 取得攝影機資料
@app.get('/server/camera/caminfo')
async def getCameraState():
    info = DB.getAllCamInfo()
    DetectManager.reflashingCamData()
    return info

# 取得攝影機資料(New)
@app.get('/server/camera/info')
async def getCameraState():
    info = DB.getAllCamInfo()
    return info

# 設置攝影機模式
@app.post('/server/camera/setmode')
async def setCameraMode(info: CameraModeInfo):
    cam_name = info.name
    cam_mode = info.mode
    try:
        if DetectManager.isProcessTerminate(cam_name):
            return {'message': 'procHasBeenKill'}
        if DB.changeCameraMode(cam_name, cam_mode):
            DetectManager.reflashingCamMode()
            return {'message': 'success'}
        return {'message': 'fail'}
    except KeyError as e:
        return {'message': f'{cam_name} Not Found!'}

# 取得執行序
@app.post('/server/camera/getproc/{name}')
async def getProcStatus(name: str):
    try:
        if DetectManager.isProcessTerminate(name):
            return {'message': f'{name} procHasBeenKill'}
        return{'message': f'{name} not been kill'}
    except KeyError as e:
        return {'message': f'{name} Not Found!'}


# 設置攝影機暫停
@app.post('/server/camera/setstate/paused')
async def setCameraPause(cam_info: CameraStateInfo):
    try:
        if DetectManager.isProcessTerminate(cam_info.name):
            return {'message': 'procHasBeenKill'}
        if DB.changeCameraStatus(cam_info.name, cam_info.state):
            DetectManager.pauseProcess(cam_info.name)
            return {'message': 'success'}
        return {'message': 'fail'}
    except KeyError as e:
        return {'message': f'{cam_info.name} Not Found!'}

# 設置攝影機開始
@app.post('/server/camera/setstate/resume')
async def setCameraResume(cam_info: CameraStateInfo):
    try:
        if not DetectManager.isProcessTerminate(cam_info.name):
            return {'message': 'procisrunning'}
        if DB.changeCameraStatus(cam_info.name, cam_info.state):
            DetectManager.resumeProcess(cam_info.name)
            return {'message': 'success'}
        return {'message': 'fail'}
    except KeyError as e:
        return {'message': f'{cam_info.name} Not Found!'}


# 刪除攝影機
@app.delete('/server/camera/delete/{name}')
async def deleteCamera(name: str):
    if DB.DeleteSingleCamera(name):
        DetectManager.deleteDetectCam(name)
        return {'message':'success'}
    return {'message': f'{name}NotFound'}

# 編輯成員
@app.put('/member/edit/{oldname}')
async def editMember(oldname: str, new_member: MemberInfo):
    # new_image = base64.b64decode(new_member.image)
    # new_avatar = base64.b64decode(new_member.avatar)
    new_image = FileManager.encodeImageToBuffer(new_member.image)
    new_avatar = FileManager.encodeImageToBuffer(new_member.avatar)

    oldimgpath = DB.getMemberImagePath(oldname)
    oldimgfilename = DB.getMemberImageFileName(oldname)

    oldavatarpath = DB.getMemberAvatarPath(oldname)
    oldavatarfilename = DB.getMemberAvatarFileName(oldname)

    try:
        FileManager.DeleteImage(path=oldimgpath, filename=oldimgfilename)
        FileManager.DeleteImage(path=oldavatarpath, filename=oldavatarfilename)
    except Exception as e:
        return {"message": f'File delete error! reason:{e}'}
    result, _ = DB.DeleteMember(oldname)
    if not result:
        return {"message": f'Database delete error!'}

    try:
        imageFileName, imagePath, avatarFileName, avatarPath = FileManager.saveImage(new_image, new_member.name, new_avatar)
    except Exception as e:
        return {"message": f'寫入檔案失敗, 原因：{e}'}
    if DB.addMemberToDatabase(name=new_member.name, imgfilename=imageFileName, avatarfilename=avatarFileName,
                              avatarpath=avatarPath, imagepath=imagePath):
        DetectManager.reflashingDetectData()
        return {"message": "success"}
    return {"message": "寫入資料庫失敗！"}



# 刪除人員
@app.delete('/member/delete/{name}')
async def deleteMember(name: str):
    suc, data = DB.DeleteMember(name)
    if suc:
        try:
            FileManager.DeleteImage(data['imgpath'], data['imgfilename'])
            FileManager.DeleteImage(data['avatarpath'], data['avatarfilename'])
        except Exception as e:
            return {'message': f'刪除檔案失敗！原因:\n{e}'}
        return {'message': f'success'}
    else:
        return {"message": "刪除失敗！原因：查無資料"}

# 新增人員
@app.post('/member/add')
async def addMember(member: MemberInfo):
    image = FileManager.encodeImageToBuffer(member.image)
    avatar = FileManager.encodeImageToBuffer(member.avatar)
    # 先儲存檔案成功再寫入資料庫
    try:
        imageFileName, imagePath, avatarFileName, avatarPath = FileManager.saveImage(image, member.name, avatar)
    except Exception as e:
        return {"message": f'寫入檔案失敗, 原因：{e}'}
    if DB.addMemberToDatabase(name=member.name, imgfilename=imageFileName, avatarfilename=avatarFileName,
                              avatarpath=avatarPath, imagepath=imagePath):
        DetectManager.reflashingDetectData()
        return {"message": "success"}
    return {"message": "寫入資料庫失敗"}

# 取得所有人員(包含檢查成員)
@app.get('/member/getAll')
async def getAllMember():
    allMember = []
    temp_avatar_list = list()
    x = 0
    y = int(4096/5)
    w = 3072
    h = 3072

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
        # encode_pic = base64.b64encode(pic).decode('utf-8')
        repic = pic[y:y+h, x:x+w]
        _, avatar_buffer = cv2.imencode('.jpg', repic)
        encode_pic = base64.b64encode(avatar_buffer).decode('utf-8')
        allMember.append({
            "name": name,
            "avatar": encode_pic
        })
    return allMember

# 取得單個可疑人士影片
@app.get('/sus/get/video/{videopath}')
async def getSUSVideo(videoname: str):
    names = DB.getAllSUSVideoNames()
    path = os.path.join(os.getcwd(), "Server", 'FileData', 'SUSPeople', "Video")
    if videoname in names:
        return FileResponse(os.path.join(path, videoname))
    else:
        return {"message": "FileNotFoundError"}

# 取得單個可疑人士照片
@app.get('/sus/get/image/{imagepath}')
async def getSUSImage(imagename: str):
    names = DB.getAllSUSImageNames()
    path = os.path.join(os.getcwd(), "Server", 'FileData', 'SUSPeople', "Image")
    if imagename in names:
        return FileResponse(os.path.join(path, imagename))
    else:
        return {"message": "FileNotFoundError"}

# 取得全部可疑人士資訊
@app.get('/sus/get/all')
async def getALLSUSMember():
    allSUS = []
    temp_sus_list = DB.getAllSUS()

    for imposter in temp_sus_list:
        # videopath = os.path.join(imposter['videoPath'], imposter['vidFilename'])
        videopath = imposter['vidFilename']
        # imagepath = os.path.join(imposter['imagePath'], imposter['imgFilename'])
        imagepath = imposter['imgFilename']
        sus = {
            "appear_time": imposter['appear'],
            "videopath": videopath,
            "imagepath": imagepath,
            "place": imposter['place']
        }
        allSUS.append(sus)
    return allSUS

@app.websocket("/ws")
async def read_webscoket(websocket: WebSocket):
    await websocket.accept()

    #     async def read_from_socket(websocket: WebSocket):
    #         nonlocal Mode
    #         async for data in websocket.iter_text():
    #             Mode = data
    #
    #     asyncio.create_task(read_from_socket(websocket))
    #     try:
    #         while True:
    #             if Mode == "Onbutton":
    #                 predict.put(dm.forRoom_faceon_detect(main_frames.get()))
    #             elif Mode == "OFF!":
    #                 predict.put(dm.forRoom_faceoff_detect(main_frames.get()))
    #             elif Mode == "Outside":
    #                 predict.put(dm.forOutDoor(main_frames.get()))
    #             print(f"Now Mode: {Mode}")
    #             _, encodedImage = cv2.imencode(".jpg", predict.get())
    #             await websocket.send_bytes(encodedImage.tobytes())
    #             await asyncio.sleep(0.01)


    print(f'與Box的websocket連接成功！')
    try:
        while True:
            raw_data = await websocket.receive_text()
            raw_time = await websocket.receive_text()
            # print(f'now is Predict!{raw_data}')
            if raw_data == "{}":
                continue
            else:
                # print(f'send Time: {raw_time}\n\n\n\n\n')
                data = eval(raw_data)
                current_time = datetime.datetime.strptime(raw_time, '%Y-%m-%d %H:%M:%S.%f')
                DetectManager.Detect(data, current_time)
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        print("Box Disconnected! reason: 'WebSocketDisconnect'\n")
        DetectManager.cleanUpAllDetectCam()
    except ConnectionClosed:
        print("Box Disconnected! reason: 'ConnectionClosed'")


if __name__ == "__main__":
    uvicorn.run("api_Server:app", reload=True)
