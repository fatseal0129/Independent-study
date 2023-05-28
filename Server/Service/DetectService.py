import base64
import threading
from collections import deque
from enum import Enum, unique
from Server.Detect import Dm
import subprocess as sp
import cv2
from Server.Service import AlertManager, DB, FileManager
import numpy as np


# 這邊可以修改或是增加模式
@unique
class Mode(str, Enum):
    Outdoor_Mode = "outdoor"
    Normal_Mode = "normal"
    Room_Mode = "room"
    Room_Outside_Mode = "room_outside"


class DetectManager:
    def __init__(self):
        # 這邊應當要與send-serverService同步
        self.CameraModeList = {}
        # 儲存Camera是否有暫停
        self.CameraState = {}

        self.deque = deque()

        self.pushProcess = dict()

        self.isReflashing = False

        self.isSusTime_outdoor = False
        self.recordingTime_outdoor = 0

        self.isSusTime_Room = False
        self.recordingTime_Room = 0

        self.isSusTime_Room_outside = False
        self.recordingTime_Room_outside = 0

        self.rtmpUrl = ""

        self.command = ['ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', f'{1280}x{720}',
                        '-r', 20,
                        '-i', '-',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'ultrafast',
                        '-f', 'flv',
                        self.rtmpUrl]

        # command = ['ffmpeg',
        #            '-y',
        #            '-f', 'rawvideo',
        #            '-vcodec', 'rawvideo',
        #            '-pix_fmt', 'bgr24',
        #            '-s', '1280*720',  # 根据输入视频尺寸填写
        #            '-r', '25',
        #            '-i', '-',
        #            '-c:v', 'h264',
        #            '-pix_fmt', 'yuv420p',
        #            '-preset', 'ultrafast',
        #            '-f', 'flv',
        #            rtmp]

        # 進行Cam刷新
        self.reflashingCamData()

        # 進行人臉刷新
        self.reflashingDetectData()



    def reflashingDetectData(self):
        """
        刷新Detect人臉資料
        :return:
        """
        self.isReflashing = True
        print("偵測到新人臉！刷新中....")
        names = DB.getAllMemberNames()
        facelist = FileManager.loadingKnowFace(filenameList=DB.getAllMemberImageFileNames(),
                                               pathList=DB.getAllMemberImagePath())
        encodelist = FileManager.encodeFace(facelist)

        Dm.reflashing(names=names, facelist=facelist, encodelist=encodelist)
        print("刷新成功！.")
        self.isReflashing = False
    def reflashingCamData(self):
        """
        刷新Cam資料
        :return:
        """
        self.isReflashing = True
        cammodes = DB.getAllCamName_with_Mode()
        camstates = DB.getAllCamName_with_State()
        for modes in cammodes:
            name = modes['name']
            mode = modes['mode']
            self.CameraModeList[name] = mode

        for states in camstates:
            name = states['name']
            state = states['state']
            self.CameraState[name] = state
            if len(self.command) > 0:
                self.pushProcess[name] = sp.Popen(self.command, stdin=sp.PIPE)
        self.isReflashing = False

    def addDetectCam(self, name, mode, status):
        """
        把Camera加入到Detect的List
        :param name:地點
        :param mode:模式
        :param status:是否為暫停
        :return:
        """
        self.CameraModeList[name] = mode
        self.CameraState[name] = status
        self.reflashingCamData()

    # def push_frame(self):
    #     # 防止多线程时 command 未被设置
    #     while True:
    #         if len(self.command) > 0:
    #             # 管道配置
    #             p = sp.Popen(self.command, stdin=sp.PIPE)
    #
    #     while True:
    #         if self.deque:
    #         # if  != True:
    #             frame = self.frame_queue.get()
    #             # process frame
    #             # 你处理图片的代码
    #             # write to pipe
    #             p.stdin.write(frame.tostring())

    def Detect(self, data, current_time):
        temp_Dict = {}
        for name, raw_frame in data.items():
            if not self.isReflashing:
                # 可能會出錯 這裡要小心
                predict = np.empty([1, 1, 1])

                frame_original = base64.b64decode(raw_frame)
                frame_as_np = np.frombuffer(frame_original, dtype=np.uint8)
                frame = cv2.imdecode(frame_as_np, flags=1)

                # frame = base64.b64encode(raw_frame)
                mode = self.CameraModeList[name]

                if mode == Mode.Room_Mode:
                    predict = self.RoomMode(frame, current_time)

                elif mode == Mode.Normal_Mode:
                    predict = self.NormalMode(frame)

                elif mode == Mode.Outdoor_Mode:
                    predict = self.OutDoorMode(frame, current_time)

                elif mode == Mode.Room_Outside_Mode:
                    predict = self.RoomOutsideMode(frame, current_time)

                else:
                    print(f'Mode not exist! {name} using Normal mode')
                    predict = self.NormalMode(frame)

                # 要實作PUSH至RTSP SERVER
                # self.deque.append(predict)
                pro = self.pushProcess[name]
                pro.stdin.write(frame.tostring())
        # return temp_Dict



    def RoomMode(self, frame, current_time):
        predict, abandoned_objects = Dm.room_mode(frame, current_time)

        if len(abandoned_objects) > 0:
            if self.isSusTime_Room is False:
                data = AlertManager.createWriter(current_time, frame)
                # 實作資料庫
                DB.addAmogus(data['id'], data['current_time'], data['output_vid_path'], data['output_img_path'],
                             data['output_vid_name'], data['output_img_name'])
                self.recordingTime_Room = current_time
                self.isSusTime_Room = True
        else:
            if self.isSusTime_Room:
                self.isSusTime_Room = False
                AlertManager.cleanSingle(self.recordingTime_Room)
            self.recordingTime_Room = current_time

        for objects in abandoned_objects:
            # id, x2, y2, w2, h2 = objects
            if self.isSusTime_Room:
                AlertManager.susWriteFrame(frame, self.recordingTime_Room)
            cv2.putText(predict, f'FIND SUS! Recording...', (500, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (34, 34, 178),
                        lineType=cv2.LINE_AA)
        return predict

    def OutDoorMode(self, frame, current_time):
        predict, abandoned_objects = Dm.outdoor_mode(frame, current_time)

        if len(abandoned_objects) > 0:
            if self.isSusTime_outdoor is False:
                data = AlertManager.createWriter(current_time, frame)
                # 實作資料庫
                DB.addAmogus(data['id'], data['current_time'], data['output_vid_path'], data['output_img_path'],
                             data['output_vid_name'], data['output_img_name'])
                self.recordingTime_outdoor = current_time
                self.isSusTime_outdoor = True
        else:
            if self.isSusTime_outdoor:
                self.isSusTime_outdoor = False
                AlertManager.cleanSingle(self.recordingTime_outdoor)
            self.recordingTime_outdoor = current_time

        for objects in abandoned_objects:
            # id, x2, y2, w2, h2 = objects
            if self.isSusTime_outdoor:
                AlertManager.susWriteFrame(frame, self.recordingTime_outdoor)
            cv2.putText(predict, f'FIND SUS! Recording...', (500, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (34, 34, 178),
                        lineType=cv2.LINE_AA)

        return predict

    def NormalMode(self, frame):
        return Dm.normal_mode(frame)

    def RoomOutsideMode(self, frame, current_time):
        predict, abandoned_objects = Dm.room_mode_goOutside(frame, current_time)

        if len(abandoned_objects) > 0 and (self.isSusTime_Room_outside is False):
            self.recordingTime_Room_outside = current_time
            data = AlertManager.createWriter(current_time, frame)
            # 實作資料庫
            DB.addAmogus(data['id'], data['current_time'], data['output_vid_path'], data['output_img_path'],
                         data['output_vid_name'], data['output_img_name'])
            self.isSusTime_Room_outside = True
        elif (current_time - self.recordingTime_Room_outside).seconds > 10:
            self.isSusTime_Room_outside = False

        if self.isSusTime_Room_outside:
            AlertManager.susWriteFrame(frame, self.recordingTime_Room_outside)
            cv2.putText(predict, f'FIND SUS! Recording...', (500, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (34, 34, 178),
                        lineType=cv2.LINE_AA)
        return predict
