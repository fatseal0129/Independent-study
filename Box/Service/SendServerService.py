import threading
# from collections import deque
from websocket import WebSocketApp
import requests
import cv2
import time
import base64
from Box.Service import CamService
import datetime

class sendService:
    def __init__(self):
        # 這邊應當要與CameraService, DetectService同步
        self.CameraModeList = {}
        # 儲存Camera是否有暫停
        self.CameraState = {}

        self.ws = None

        self.camservice = None
        self.isUsingNum = False
        self.camNum = 0


        self.wsurl = "ws://127.0.0.1:8000/ws"
        self.addcamurl = 'http://127.0.0.1:8000/server/add/Detect'

        self.pausedcamurl = 'http://127.0.0.1:8000/server/camera/setstate/paused'
        self.resumecamurl = 'http://127.0.0.1:8000/server/camera/setstate/resume'

        self.getcamstateurl = 'http://127.0.0.1:8000/server/camera/stateinfo'
        self.getcammodeurl = 'http://127.0.0.1:8000/server/camera/modeinfo'

        self.loadCamera()
        print('[SendService] Camera Loading完成！')
        time.sleep(1)

        websocket_created = threading.Thread(target=self.createWebSocket)
        websocket_created.daemon = True
        websocket_created.start()

    def createWebSocket(self):
        print("[SendService] 啟動websocket連接...")
        self.ws = WebSocketApp(self.wsurl,
                               on_open=self.on_open,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        self.ws.run_forever()

    def createConnect_to_Server(self, name: str, mode: str, url: str, state: bool):
        """
        建立與伺服器的連接
        :param name: 名字
        :param mode: 模式
        :param url: 網址
        :param state: 暫停狀態
        :return:
        """
        data = {
            "name": name,
            "mode": mode,
            "state": state,
            "url": url
        }
        r = requests.post(url=self.addcamurl, json=data)
        if r.status_code == 200:
            self.CameraModeList[name] = mode
            self.CameraState[name] = state
            self.camNum += 1
        else:
            raise Exception(f'[SendService] 與伺服器創建連接失敗! Status.code:{r.status_code}\n Reason: {r.text}')

    def on_message(self, ws, message):
        """
        接收到的Frame做處理,data={name:img(b64)}
        實作推流至RTMP伺服器
        :param ws:
        :param message:
        :return:
        """
        pass

    def on_error(self, ws, error):
        print("####### on_error #######")
        print(f'error: {error}')

    def on_close(self, ws, close_status_code, close_msg):
        print("####### on_close #######")

    def on_open(self, ws):
        print("[SendService] 與Server連接成功！ 開啟傳送通道...")
        self.camservice = CamService.CameraManager()
        # 與server連接的thread
        connection_server = threading.Thread(target=self.sendmsg_server)
        connection_server.daemon = True
        connection_server.start()

    def sendmsg_server(self):
        while True:
            if self.camNum > 0:
                now_current_time = datetime.datetime.now()
                current_time = now_current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                cameraList = {}
                for camera_name in self.CameraModeList.keys():
                    # print(f'傳送raw_frame:{camera_name}')
                    # 是否驗證成功
                    online = self.camservice.getCamStatus_online(camera_name)
                    # 是否是暫停狀態
                    state = self.camservice.getCamStatus_paused(camera_name)
                    # 檢查驗證狀況
                    if not online:
                        print(f'[SendService] 目前{camera_name}等待驗證中，10秒後重試...')
                        time_end = time.time() + 10
                        while time.time() < time_end:
                            temp_online = self.camservice.getCamStatus_online(camera_name)
                            if temp_online:
                                print(f'[SendService] {camera_name}驗證成功！ 開始傳送Frame...')
                                break
                    # 檢查暫停情況
                    elif state:
                        print(f'[SendService] 目前{camera_name}正暫停作業中，20秒自動檢查...')
                        time_end = time.time() + 20
                        while time.time() < time_end:
                            temp_state = self.camservice.getCamStatus_paused(camera_name)
                            if not temp_state:
                                self.CameraState[camera_name] = temp_state
                                print(f'[SendService] {camera_name}已啟用！ 開始傳送Frame...')
                                break
                    elif online:
                        raw_frame = self.camservice.getCleanCameraFrame(camera_name)
                        # frame = base64.b64decode(raw_frame).decode('utf-8')
                        _, frame_buffer = cv2.imencode('.jpg', raw_frame)
                        fix_frame = base64.b64encode(frame_buffer).decode('utf-8')
                        cameraList[camera_name] = fix_frame
                # 這時資料會裝著 {camName : frame(b64)}
                self.ws.send(str(cameraList))
                self.ws.send(current_time)
                # 是否要停止
            else:
                time_end = time.time() + 1
                while time.time() < time_end:
                    continue

    def loadCamera(self):
        raw_state = requests.get(url=self.getcamstateurl)
        if raw_state.status_code == 200:
            cam_state = raw_state.json()
            for state in cam_state:
                name = state['name']
                state = state['state']
                self.CameraState[name] = state
        else:
            raise Exception(f'[SendService] 取得CamState失敗！statusCode:{raw_state.status_code}\nReason{raw_state.reason}')

        raw_mode = requests.get(url=self.getcammodeurl)
        if raw_mode.status_code == 200:
            cam_mode = raw_mode.json()
            for mode in cam_mode:
                name = mode['name']
                mode = mode['mode']
                self.CameraModeList[name] = mode
                self.camNum += 1
        else:
            raise Exception(f'[SendService] 取得Mode失敗！statusCode:{raw_mode.status_code}\nReason{raw_mode.reason}')

    def changeCameraPaused(self, name):
        print(f'[SendService] {name} 準備暫停！')
        self.camservice.pauseCamera(name)
        # request
        data = {
            "name": name,
            "state": True,
        }
        r = requests.post(url=self.pausedcamurl, json=data)
        if r.status_code == 200:
            pass
            self.CameraState[name] = True
        else:
            raise Exception(f'[SendService] 與伺服器溝通「暫停」失敗! Status.code:{r.status_code}\n Reason: {r.text}')



    def changeCameraResume(self, name):
        print(f'[SendService] {name} 準備開始！')
        self.camservice.resumeCamera(name)
        # request
        data = {
            "name": name,
            "state": False,
        }
        r = requests.post(url=self.resumecamurl, json=data)
        if r.status_code == 200:
            self.CameraState[name] = False
        else:
            raise Exception(f'[SendService] 與伺服器溝通「開始」失敗! Status.code:{r.status_code}\n Reason: {r.text}')

    def changeCameraMode(self, name, changed_mode):
        pass

    def cleanConnection(self, name):
        data = {
            "name": name
        }
        r = requests.post(url=self.addcamurl, json=data)
        if r.status_code == 200:
            del self.CameraModeList[name]
            del self.CameraState[name]
            self.camNum -= 1
            print(f'[SendService] {name} 清除連線成功！')
        else:
            raise Exception(f'[SendService] 伺服器端溝通「刪除」失敗! Status.code:{r.status_code}\n Reason: {r.text}')


    def cleanAllConnection(self):
        pass
