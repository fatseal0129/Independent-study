import sys

import Box.Camera.Camera as cam
import cv2
import base64
import requests
from requests.exceptions import ConnectionError
class CameraManager:
    def __init__(self):
        self.CameraList = {}
        # self.getcaminfourl = 'http://140.118.110.201:8000/server/camera/caminfo'
        self.getcaminfourl = 'http://211.21.74.23:8000/server/camera/caminfo'
        # self.getcaminfourl = 'http://127.0.0.1:8000/server/camera/caminfo'
        self.loadCamera()

    def loadCamera(self):
        try:
            raw_state = requests.get(url=self.getcaminfourl)
            if raw_state.status_code == 200:
                cam_state = raw_state.json()
                for camera in cam_state:
                    name = camera['name']
                    mode = camera['mode']
                    url = camera['url']
                    if url == "0":
                        self.createCamera(0, name, mode)
                    else:
                        self.createCamera(url, name, mode)
            else:
                print(f'[CameraService] 取得camInfo失敗！statusCode:{raw_state.status_code}\nReason:{raw_state.reason}')
        except ConnectionError as e:
            print(f'[CameraService] Loading Camera失敗！ Server尚未開啟？')


    def getCleanCameraFrame(self, name):
        """
        取得單一攝影機的Frame
        :param name: 名字/場地
        :return:
        """
        camera = self.CameraList[name]
        return camera.getFrame()

    def getScreenShot(self, name):
        camera = self.CameraList[name]
        frame = camera.getFirstFrame()
        _, frame_buffer = cv2.imencode('.jpg', frame)
        str_frame = base64.b64encode(frame_buffer).decode('utf-8')
        return str_frame

    def getCamStatus_paused(self, name):
        camera = self.CameraList[name]
        return camera.getStatus_paused()

    def getCamStatus_online(self, name):
        camera = self.CameraList[name]
        return camera.getStatus_online()

    def resumeCamera(self, name):
        """
        恢復單一攝影機的運行
        :param name: 名字/場地
        :return:
        """
        camera = self.CameraList[name]
        camera.resume()

    def pauseCamera(self, name):
        """
        暫停單一攝影機的運行
        :param name: 名字/場地
        :return:
        """
        camera = self.CameraList[name]
        camera.pause()

    def createCamera(self, url, name, initial_mode):
        """
        創建一個新的攝影機，剛創建的攝影機都會是暫停狀態
        :param url: 連接網址
        :param name: 名字/場地
        :param initial_mode: 剛開始的模式
        :return:
        """
        print(f'[CameraService] 建立新的Camera name: {name}, url: {url}')

        # 新增Camera
        self.CameraList[name] = cam.Camera(url, initial_mode)
        # 開啟Camera 這邊要考慮是否要暫停
        self.CameraList[name].start()


    def cleanCamera(self, name):
        """
        刪除單一攝影機
        :param name:名字/場地
        :return:
        """
        camera = self.CameraList[name]
        camera.cleanUP()
        del self.CameraList[name]


