import base64
import threading
from collections import deque
from enum import Enum, unique
from Detect import dm
import cv2
import Service.AlertService
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

        ## 之後要實作Loading資料庫


        self.alert = Service.AlertService.AlertSUS()

        self.isSusTime_outdoor = False
        self.recordingTime_outdoor = 0

        self.isSusTime_Room = False
        self.recordingTime_Room = 0

        self.isSusTime_Room_outside = False
        self.recordingTime_Room_outside = 0

    def addDetectCam(self, name, mode, status):
        """
        把Camera加入到Detect的List
        :param name:名字
        :param mode:模式
        :param status:是否為暫停
        :return:
        """
        self.CameraModeList[name] = mode
        self.CameraState[name] = status

    def Detect(self, data, current_time):
        temp_Dict = {}
        for name, raw_frame in data.items():
            # 可能會出錯 這裡要小心
            predict = np.empty([1, 1, 1])
            frame = base64.b64encode(raw_frame)
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
            # temp_Dict[name] = base64.b64decode(predict)
        #return temp_Dict


    def RoomMode(self, frame, current_time):
        predict, abandoned_objects = dm.room_mode(frame, current_time)

        if len(abandoned_objects) > 0:
            if self.isSusTime_Room is False:
                self.alert.createWriter(current_time, frame)
                self.recordingTime_Room = current_time
                self.isSusTime_Room = True
        else:
            if self.isSusTime_Room:
                self.isSusTime_Room = False
                self.alert.cleanSingle(self.recordingTime_Room)
            self.recordingTime_Room = current_time

        for objects in abandoned_objects:
            #id, x2, y2, w2, h2 = objects
            if self.isSusTime_Room:
                self.alert.susWriteFrame(frame, self.recordingTime_Room)
            cv2.putText(predict, f'FIND SUS! Recording...', (500, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (34, 34, 178),
                        lineType=cv2.LINE_AA)
        return predict


    def OutDoorMode(self, frame, current_time):
        predict, abandoned_objects = dm.outdoor_mode(frame, current_time)

        if len(abandoned_objects) > 0:
            if self.isSusTime_outdoor is False:
                self.alert.createWriter(current_time, frame)
                self.recordingTime_outdoor = current_time
                self.isSusTime_outdoor = True
        else:
            if self.isSusTime_outdoor:
                self.isSusTime_outdoor = False
                self.alert.cleanSingle(self.recordingTime_outdoor)
            self.recordingTime_outdoor = current_time

        for objects in abandoned_objects:
            # id, x2, y2, w2, h2 = objects
            if self.isSusTime_outdoor:
                self.alert.susWriteFrame(frame, self.recordingTime_outdoor)
            cv2.putText(predict, f'FIND SUS! Recording...', (500, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (34, 34, 178),
                        lineType=cv2.LINE_AA)

        return predict

    def NormalMode(self, frame):
        return dm.normal_mode(frame)

    def RoomOutsideMode(self, frame, current_time):
        predict, abandoned_objects = dm.room_mode_goOutside(frame, current_time)

        if len(abandoned_objects) > 0 and (self.isSusTime_Room_outside is False):
            self.recordingTime_Room_outside = current_time
            self.alert.createWriter(current_time, frame)
            self.isSusTime_Room_outside = True
        elif (current_time - self.recordingTime_Room_outside).seconds > 10:
            self.isSusTime_Room_outside = False

        if self.isSusTime_Room_outside:
            self.alert.susWriteFrame(frame, self.recordingTime_Room_outside)
            cv2.putText(predict, f'FIND SUS! Recording...', (500, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (34, 34, 178),
                        lineType=cv2.LINE_AA)
        return predict
