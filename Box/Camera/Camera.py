import cv2
# import datetime
import time
import threading
from collections import deque

class Camera(threading.Thread):
    def __init__(self, url, initial_mode):
        super(Camera, self).__init__()

        # 用來存放frame的deque
        self.deque = deque()
        # 攝影機連接
        self.url = url
        # 攝影機初始模式
        self.mode = initial_mode

        self.online = False
        self.capture = None

        self.daemon = True
        # 剛開始狀態為 paused.
        self.paused = True
        self.state = threading.Condition()

        # 開啟攝影機
        self.load_network_stream()

    def load_network_stream(self):
        """
        驗證url，如果有效就打開
        """
        print(f'驗證攝影機: {self.url} ...')
        def load_network_stream_thread():
            if self.verify_network_stream(self.url):
                self.capture = cv2.VideoCapture(self.url)
                self.online = True
                print(f'攝影機{self.url}驗證成功！')

        self.load_stream_thread = threading.Thread(target=load_network_stream_thread, args=())
        self.load_stream_thread.daemon = True
        self.load_stream_thread.start()

    def verify_network_stream(self, url):
        """
        試圖從url中接收一frame來測試
        """

        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            print(f'驗證攝影機失敗！')
            return False
        cap.release()
        return True

    def getStatus_paused(self) -> bool:
        """
        攝影機目前是否為暫停狀態
        :return: bool
        """
        return self.paused

    def getStatus_online(self) -> bool:
        """
        攝影機是否上線(驗證成功並可以使用)
        :return: bool
        """
        return self.online

    def getMode(self):
        """
        取得攝影機目前的模式
        :return: 模式 -> str
        """
        return self.mode

    def run(self):
        while True:
            # 先檢查是否為暫停狀態
            with self.state:
                if self.paused:
                    print(f'{self.url} 暫停中....')
                    self.state.wait()  # 暫停運行，直到得到通知.
            # Do stuff...
            try:
                if self.capture.isOpened() and self.online:
                    # Read next frame from stream and insert into deque
                    status, frame = self.capture.read()
                    if status:
                        self.deque.append(frame)
                    else:
                        self.capture.release()
                        self.online = False
                else:
                    # 代表斷開 嘗試重新連接
                    print(f'連接{self.url}斷開！ 嘗試重新連線')
                    self.load_network_stream()
                    self.spin(2)
                self.spin(.001)
            except AttributeError:
                pass

    def pause(self):
        with self.state:
            self.paused = True  # Block self.

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # Unblock self if waiting.
            print(f'{self.url} 開始運行....')

    def getFrame(self):
        if not self.online:
            self.spin(1)
            return

        if self.deque and self.online:
            return self.deque[-1]

    def spin(self, seconds):
        """
        要暂停多久，取代time.sleep，這樣程序才不會停止。
        :param seconds: 要暫停的秒數
        :return:
        """

        # endTime = datetime.datetime.now().second + seconds
        # print(f'now spin waiting for {seconds} seconds')
        # while datetime.datetime.now().second < endTime:
        #     continue
        # print('done waiting!')
        time_end = time.time() + seconds
        while time.time() < time_end:
            continue

    def cleanUP(self):
        self.deque.clear()
        self.online = False
        self.capture.release()
        print(f'連接{self.url}已關閉！')
