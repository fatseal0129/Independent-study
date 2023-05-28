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

        self.camservice = None
        self.isUsingNum = False
        self.camNum = 0


        self.wsurl = "ws://127.0.0.1:8000/ws"
        self.postcamurl = 'http://127.0.0.1:8000/server/add/Detect'

        self.getcamstateurl = 'http://127.0.0.1:8000/server/camera/stateinfo'
        self.getcammodeurl = 'http://127.0.0.1:8000/server/camera/modeinfo'

        self.loadCamera()

        time.sleep(1)

        self.ws = WebSocketApp(self.wsurl,
                               on_open=self.on_open,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        print("啟動websocket連接...")
        self.ws.run_forever()

    def createConnect_to_Server(self, name: str, mode: str, url: str, state: bool):
        data = {
            "name": name,
            "mode": mode,
            "state": state,
            "url": url
        }
        r = requests.post(url=self.postcamurl, json=data)
        if r.status_code == 200:
            self.CameraModeList[name] = mode
            self.CameraState[name] = state
            self.camNum += 1
        else:
            raise Exception(f'與伺服器創建連接失敗! Status.code:{r.status_code}\n Reason: {r.text}')

    def on_message(self, ws, message):
        """
        接收到的Frame做處理,data={name:img(b64)}
        實作推流至RTMP伺服器
        :param ws:
        :param message:
        :return:
        """
        pass
        #raw_data = message
        #data = eval(raw_data)


    def on_error(self, ws, error):
        print("####### on_error #######")
        print("error：%s" % error)

    def on_close(self, ws, close_status_code, close_msg):
        print("####### on_close #######")

    def on_open(self, ws):
        print("與Server連接成功！ 開啟傳送通道...")
        self.camservice = CamService.CameraManager()
        # 與server的thread
        connection_server = threading.Thread(target=self.sendmsg_server)
        connection_server.daemon = True
        connection_server.start()

    def sendmsg_server(self):
        print('開始傳送Frame至Server')
        while True:
            if self.camNum > 0:
                current_time = datetime.datetime.now()
                cameraList = {}
                for camera_name in self.CameraModeList.keys():
                    if self.CameraState[camera_name] is False:
                        raw_frame = self.camservice.getCleanCameraFrame(camera_name)
                        frame = base64.b64decode(raw_frame).decode('utf-8')
                        _, frame_buffer = cv2.imencode('.jpg', frame)
                        fix_frame = base64.b64encode(frame_buffer).decode('utf-8')
                        cameraList[camera_name] = fix_frame
                # 這時資料會裝著 {camName : frame(b64)}
                self.ws.send(str(cameraList))
                self.ws.send(str(current_time))
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
            raise Exception(f'取得State失敗！statusCode:{raw_state.status_code}\nReason{raw_state.reason}')

        raw_mode = requests.get(url=self.getcammodeurl)
        if raw_mode.status_code == 200:
            cam_mode = raw_mode.json()
            for mode in cam_mode:
                name = mode['name']
                mode = mode['mode']
                self.CameraModeList[name] = mode
                self.camNum += 1
        else:
            raise Exception(f'取得Mode失敗！statusCode:{raw_mode.status_code}\nReason{raw_mode.reason}')


    def changeCameraMode(self, name, changed_mode):
        pass

    def cleanConnection(self, name):
        pass

    def cleanAllConnection(self):
        pass
