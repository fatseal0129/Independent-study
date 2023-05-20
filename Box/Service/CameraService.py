import Box.Camera.Camera as cam
import requests
class CameraManager:
    def __init__(self):
        self.CameraList = {}
        self.getcamstateurl = 'http://127.0.0.1:8000/server/camera/caminfo'
        self.loadCamera()
    def loadCamera(self):
        raw_state = requests.get(url=self.getcamstateurl)
        if raw_state.status_code == 200:
            cam_state = raw_state.json()
            for cam in cam_state:
                name = cam['name']
                mode = cam['mode']
                url = cam['url']
                self.createCamera(url, name, mode)
        else:
            print(f'取得State失敗！statusCode:{raw_state.status_code}\nReason{raw_state.reason}')

        pass

    def getCleanCameraFrame(self, name):
        """
        取得單一攝影機的Frame
        :param name: 名字/場地
        :return:
        """
        return self.CameraList[name].getFrame()

    def getCamStatus_paused(self, name):
        return self.CameraList[name].getStatus_paused()

    def resumeCamera(self, name):
        """
        恢復單一攝影機的運行
        :param name: 名字/場地
        :return:
        """
        self.CameraList[name].resume()

    def pauseCamera(self, name):
        """
        暫停單一攝影機的運行
        :param name: 名字/場地
        :return:
        """
        self.CameraList[name].pause()

    def createCamera(self, url, name, initial_mode):
        """
        創建一個新的攝影機，剛創建的攝影機都會是暫停狀態
        :param url: 連接網址
        :param name: 名字/場地
        :param initial_mode: 剛開始的模式
        :return:
        """
        print(f'create Camera name: {name}, url: {url}')

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
        try:
            self.CameraList[name].cleanUP()
            return True
        except Exception:
            return False
