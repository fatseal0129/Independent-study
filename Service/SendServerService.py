import threading
from collections import deque
from websocket import WebSocketApp
import requests
import time
import base64
import Service.CameraService
import datetime

class sendService:
    def __init__(self):
        # 這邊應當要與CameraService, DetectService同步
        self.CameraModeList = {}
        # 儲存Camera是否有暫停
        self.CameraState = {}

        self.camservice = None

        self.camNum = 0

        # 實作loadCamera 之後資料都要與資料庫對接
        ####
        ####

        # 之後要改的
        self.wsurl = "ws://127.0.0.1:8000/ws"
        self.posturl = 'http://127.0.0.1:8000/server/add/Detect'

        self.ws = WebSocketApp(self.wsurl,
                               on_open=self.on_open,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        print("啟動websocket連接...")
        self.ws.run_forever()

    def createConnect_to_Server(self, name:str, mode:str, state:bool):
        data = {
            "name": name,
            "mode": mode,
            "state": state
        }
        r = requests.post(url=self.posturl, json=data)
        if r.status_code == 200:
            self.CameraModeList[name] = mode
            self.CameraState[name] = state
            self.camNum += 1
        else:
            print(f'加入失敗！statusCode:{r.status_code}\nReason{r.reason}')

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
        self.camservice = Service.CameraService.CameraManager()
        print("與Server連接成功！ 開啟傳送通道...")
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
                        frame = base64.b64decode(raw_frame)
                        cameraList[camera_name] = frame
                # 這時資料會裝著 {camName : frame(b64)}
                self.ws.send(str(cameraList))
                self.ws.send(str(current_time))

    def loadCamera(self):
        pass

    def changeCameraMode(self, name, changed_mode):
        pass

    def cleanConnection(self, name):
        pass

    def cleanAllConnection(self):
        pass
