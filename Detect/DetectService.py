# import threading
class DetectManager:
    def __init__(self):
        self.CameraList = {}

    def getCleanCameraFrame(self, name):
        """
        取得單一攝影機的Frame
        :param name: 名字/場地
        :return:
        """
        return self.CameraList[name].getFrame()

    def getPredictedCameraFrame(self, name):
        """
        取得已經預測完的frame
        :param name:
        :return:
        """
        frame = self.CameraList[name]

    def getStatus(self, name):
        return self.CameraList[name].getStatus()

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

    def createCamera(self, url, name, initial_mode) -> bool:
        """
        創建一個新的攝影機，剛創建的攝影機都會是暫停狀態
        :param url: 連接網址
        :param name: 名字/場地
        :param initial_mode: 剛開始的模式
        :return:
        """
        try:
            print(f'create Camera name: {name}, url: {url}')
            # 新增影片Writer
            self.CameraList[name] = cam.Camera(url, initial_mode)
            # 開啟攝影機
            self.CameraList[name].start()
            return True
        except Exception:
            return False

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
