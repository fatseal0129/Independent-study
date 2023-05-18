import threading
import base64
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from fastapi.responses import StreamingResponse
from websockets.exceptions import ConnectionClosed
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Detect import dm
import Service
from Service import CameraManager
import cv2
from vidgear.gears import CamGear

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Mode_Room(threading.Thread):
    def __init__(self, p, m):
        super(Mode_Room, self).__init__()
        self.predictQueue = p
        self.mainframe = m
        self.daemon = True  # Allow main to exit even if still running.
        self.paused = True  # Start out paused.
        self.state = threading.Condition()

    def run(self):
        while True:
            with self.state:
                if self.paused:
                    self.state.wait()  # Block execution until notified.
            # Do stuff...
            frame = self.mainframe.get()
            self.predictQueue.put(dm.forRoom_faceon_detect(frame))

    def pause(self):
        with self.state:
            self.paused = True  # Block self.
            #rlock.release()

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # Unblock self if waiting.
# 新增攝影機
@app.post('camera/add')
async def AddCamera(response):
    name = response['name']
    url = response['url']
    init_mode = response['mode']
    pass


# 拿取全部可疑人士
@app.get('sus/get/all')
async def getALLSUSMember():
    pass


# 顯示成員
@app.get('/member/get')
async def getAllMember():
    allMember = []
    avatarList, nameList = Service.FileService.loadingKnowAvatar()
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
    if Service.FileService.saveImage(image, name, avatar):
        return {"message": "success!"}
    else:
        return {"message": "Fail!"}

# 編輯成員
@app.post('/member/edit')
async def editMember(response):
    pass

# 檢查成員


# 更改模式
@app.websocket("/ws")
async def read_webscoket(websocket: WebSocket):
    await websocket.accept()
    await websocket.receive_text()

    global main_frames
    global predicted

    camera_thread = threading.Thread(target=main_stream, args=(main_frames,), daemon=True)
    camera_thread.start()

    room_mode = Mode_Room(predicted, main_frames)
    room_mode.start()

    # async def read_from_socket(websocket: WebSocket):
    #     nonlocal Mode
    #     async for data in websocket.iter_text():
    #         Mode = data
    #
    # asyncio.create_task(read_from_socket(websocket))
    try:
        while True:
            Mode = await websocket.receive_text()
            if Mode == "room":
                if not out_mode.paused:
                    out_mode.pause()
                room_mode.resume()
            elif Mode == "out":
                if not room_mode.paused:
                    room_mode.pause()
                out_mode.resume()

    except WebSocketDisconnect:
        print("Exit LA!!!!!!!!!")
    except ConnectionClosed:
        print("client exit")
    except Exception:
        print("client exit")
    finally:
        main_frames.empty()

# 主要Stream
def main_stream(main_frames):
    options = {'THREADED_QUEUE_MODE': True}
    cap = CamGear(source=0, logging=True, **options).start()
    while True:
        frame = cap.read()
        main_frames.put(frame)
        time.sleep(.01)

# 傳送已偵測完影像
@app.get("/")
async def video_feed():
    # 從predict拿出的 generator
    def streamer():
        try:
            while predicted:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       bytearray(predicted.get()) + b'\r\n')
        except GeneratorExit:
            print("cancelled")
    return StreamingResponse(streamer(), media_type="multipart/x-mixed-replace;boundary=frame")

if __name__ == "__main__":
    print("done")
    uvicorn.run("oldAPI:app", reload=True)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     #await connect_manager.connect(websocket)
#     await websocket.accept()
#     #global manager
#
#     #t = threading.Thread(target=start_stream, args=(manager,), daemon=True)
#     #t.start()
#
#     try:
#         while manager:
#             await websocket.send_bytes(bytearray(manager.get()))
#     except WebSocketDisconnect:
#         connect_manager.disconnect(websocket)


#
# def outside(manager, qwer):
#     while qwer.any():
#         frame = qwer
#         predict = dm.forRoom_faceoff_detect(frame)
#         _, encodedImage = cv2.imencode(".jpg", predict)
#         manager.put(encodedImage)


#
# @app.websocket("/")
# async def webVideo(websocket: WebSocket):
#     await websocket.accept()
#     cap = cv2.VideoCapture(0)
#     try:
#         print(f"使用者進入！")
#         while True:
#             _, frame = cap.read()
#             _, encoded = cv2.imencode('.jpg', frame)
#             await websocket.send_bytes(encoded.tobytes())
#     except WebSocketDisconnect:
#         print("Exit LA!!!!!!!!!")
#         cap.release()
#     except exceptions.ConnectionClosed:
#         print("client exit")
#         cap.release()


#
# @app.websocket("/detect/faceoff")
# async def faceoff(websocket: WebSocket):
#     await websocket.accept()
#     print("使用者進入室內偵測模式 - 臉部偵測「關閉」")
#     options = {'THREADED_QUEUE_MODE': True}
#     cap = CamGear(source=0, logging=True, **options).start()
#     try:
#         while True:
#             frame = cap.read()
#             predict_image = dm.forRoom_faceoff_detect(frame)
#             _, encoded = cv2.imencode('.jpg', predict_image)
#             await websocket.send_bytes(encoded.tobytes())
#     except ConnectionClosed:
#         print("Error - ConnectionClosed")
#         cap.stop()


################################# 分隔線

# main_frames = queue.Queue()
#
# @app.websocket("/ws")
# async def read_webscoket(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.receive_text()
#
#     global main_frames
#     predict = queue.Queue()
#     t_main = threading.Thread(target=main_stream, args=(main_frames,), daemon=True)
#     t_main.start()
#
#     Mode = await websocket.receive_text()
#
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
#     except WebSocketDisconnect:
#         print("Exit LA!!!!!!!!!")
#     except ConnectionClosed:
#         print("client exit")
#     except Exception:
#         print("client exit")
#     finally:
#         main_frames.empty()
#         predict.empty()
#
#
# def main_stream(main_frames):
#     options = {'THREADED_QUEUE_MODE': True}
#     cap = CamGear(source=0, logging=True, **options).start()
#     while True:
#         frame = cap.read()
#         main_frames.put(frame)
#         time.sleep(0.01)


