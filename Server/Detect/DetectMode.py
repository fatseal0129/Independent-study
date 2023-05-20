import cv2
import face_recognition
import cvzone
from ultralytics import YOLO
import math
from Server.sort import *
import os
from datetime import datetime


class DetectMode:
    def __init__(self):
        # 載入偵測「人臉」model
        self.model_faceDetectOnly = YOLO(os.path.join(os.path.dirname(os.getcwd()), 'yolo-weights', 'yolov8n-face.pt'))

        # 讀取偵測「人臉」model的class名稱
        self.classNames_faceDetectOnly = self.model_faceDetectOnly.names

        # 載入偵測「人體」model
        self.model_PersonDetectOnly = YOLO(os.path.join(os.path.dirname(os.getcwd()), 'yolo-weights', 'yolov8n.pt'))

        # 讀取偵測「人體」model的class名稱
        self.classNames_PersonDetectOnly = self.model_PersonDetectOnly.names

        # Tracking instance
        self.tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

        # 外出模式要偵測的東西
        self.newclass = ["backpack", "umbrella",
                         "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
                         "baseball bat",
                         "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                         "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                         "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                         "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                         "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                         "teddy bear", "hair drier", "toothbrush"]

        self.moved_temp = {}
        self.center_points_moved = {}

        # 儲存偵測到物件的中心點 {id : [x,y]}
        self.center_points = {}

        self.center_points_face = {}
        self.abandoned_temp_face = {}
        self.susLimitTime_face = 10

        # 保留ID的 counts （counts作為偵測是否停留太久）
        # 當有新物件的id被檢測到會被賦予新的id 這個作為目前id的計數器
        self.SUSFace_id_count = 0

        # 保留ID的 counts （counts作為偵測是否停留太久）
        # 當有新物件的id被檢測到會被賦予新的id 這個作為目前id的計數器
        # self.id_count = 0

        self.abandoned_temp = {}

        # ID持續多久(秒)會變成可疑人物
        self.susLimitTime = 20

        # 取得所有人名
        self.existfaceName = []
        # 取得所有人臉照片
        self.existFaceList = []

        # encode所有人臉
        self.existFaceEncoding = []

    def reflashing(self, names, facelist, encodelist):
        """
        刷新目前存在的臉跟encoding
        :return:
        """
        # 取得所有人名
        self.existfaceName = names
        # 取得所有人臉照片
        self.existFaceList = facelist

        # encode所有人臉
        self.existFaceEncoding = encodelist
    def outdoor_mode(self, origin_image, current_time):
        """
        戶外模式
        """
        # Objects boxes and ids
        objects_bbs_ids = []
        abandoned_object = []

        fix_img = origin_image
        perFrame = self.model_PersonDetectOnly(origin_image, stream=True)

        # 傳入np array(x1,y1,x2,y2,score) 回傳ID number與np array
        detections = np.empty((0, 5))

        for frame in perFrame:
            boxes = frame.boxes
            for box in boxes:
                # 取得座標
                x1, y1, x2, y2 = box.xyxy[0]

                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                conf = math.ceil((box.conf[0] * 100)) / 100

                # 取得classID
                classId = int(box.cls[0])

                currentClass = self.classNames_PersonDetectOnly[classId]

                # print(currentClass, conf)
                if currentClass == "person" and conf > 0.35:
                    currentArray = np.array([x1, y1, x2, y2, conf])
                    detections = np.vstack((detections, currentArray))

        result_Tracker = self.tracker.update(detections)

        for resul2t in result_Tracker:
            x1, y1, x2, y2, Id = resul2t
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            # cvzone.cornerRect(fix_img, (x1, y1, w, h), l=7, rt=2, colorR=(255, 0, 0))
            # cvzone.putTextRect(fix_img, f' {int(Id)}', (max(0, x1), max(35, y1 - 20)),
            #                    scale=2, thickness=3, offset=10)

            # 中心點
            cx = (x1 + x1 + w) / 2
            cy = (y1 + y1 + h) / 2

            # 檢查物體是否已經被檢測到
            same_object_detected = False
            for id, pt in self.center_points.items():
                if id == Id:
                    # update the center point
                    self.center_points[id] = (cx, cy)

                    objects_bbs_ids.append([x1, y1, w, h, id])
                    same_object_detected = True

                    #   Add same object to the abandoned_temp dictionary. if the object is
                    #   still in the temp dictionary for certain threshold count then
                    #   the object will be considered as abandoned object
                    if id in self.abandoned_temp:
                        # if self.abandoned_temp[id] > 100:
                        if (datetime.now() - self.abandoned_temp[id]).seconds > self.susLimitTime:
                            abandoned_object.append([id, x1, y1, w, h])
                        else:
                            # Increase count for the object
                            # self.abandoned_temp[id] += 1
                            print(
                                f'now the object has exist for: {(datetime.now() - self.abandoned_temp[id]).seconds} seconds')
                    break

            if same_object_detected is False:
                self.center_points[Id] = (cx, cy)
                # Add new object with initial count 1
                # self.abandoned_temp[Id] = 1
                self.abandoned_temp[Id] = current_time
                objects_bbs_ids.append([x1, y1, w, h, Id])

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        abandoned_temp_2 = {}

        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]

            new_center_points[object_id] = center

            if object_id in self.abandoned_temp:
                # counts = self.abandoned_temp[object_id]
                # abandoned_temp_2[object_id] = counts
                temp_time = self.abandoned_temp[object_id]
                abandoned_temp_2[object_id] = temp_time

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        self.abandoned_temp = abandoned_temp_2.copy()

        # cvzone.cornerRect(fix_img, (x1, y1, w, h), l=7, rt=2, colorR=(255, 0, 0))
        # cvzone.putTextRect(fix_img, f' {int(Id)}', (max(0, x1), max(35, y1 - 20)),
        #                    scale=2, thickness=3, offset=10)

        # cvzone.cornerRect(fix_img, (40, 90, 50, 50), l=7, rt=2, colorR=(255, 0, 0))
        cvzone.putTextRect(fix_img, datetime.now().strftime('%y-%m-%d_%H:%M:%S'), (20, 50), scale=1, thickness=1,
                           colorT=(255, 255, 255), colorR=(0, 0, 0), font=cv2.FONT_HERSHEY_COMPLEX)
        # cv2.putText(fix_img, datetime.now().strftime('%y-%m-%d_%H:%M:%S'), (40, 90), cv2.FONT_HERSHEY_COMPLEX, 1.2,
        #             (255, 255, 255), lineType=cv2.LINE_AA)

        # cv2.rectangle(self.frame, (self.screen_width - 190, 0), (self.screen_width, 50), color=(0, 0, 0),
        #               thickness=-1)
        # cv2.putText(self.frame, datetime.now().strftime('%H:%M:%S'), (self.screen_width - 185, 37),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), lineType=cv2.LINE_AA)

        return fix_img, abandoned_object

    def normal_mode(self, origin_image):
        """
        一般模式
        :param image: 傳進來的原始圖片 (PerFrame）
        :return: 偵測完的圖片 (PerFrame)
        """
        fix_img = origin_image
        #perFrame = self.model_PersonDetectOnly(origin_image, stream=True)

        # 傳入np array(x1,y1,x2,y2,score) 回傳ID number與np array
        #detections = np.empty((0, 5))

        # for frame in perFrame:
        #     boxes = frame.boxes
        #     for box in boxes:
        #         # 取得座標
        #         x1, y1, x2, y2 = box.xyxy[0]
        #
        #         x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        #
        #         conf = math.ceil((box.conf[0] * 100)) / 100
        #
        #         # 取得classID
        #         classId = int(box.cls[0])
        #
        #         currentClass = self.classNames_PersonDetectOnly[classId]
        #
        #         # print(currentClass, conf)
        #         if currentClass == "person" and conf > 0.35:
        #             currentArray = np.array([x1, y1, x2, y2, conf])
                    #detections = np.vstack((detections, currentArray))

        # result_Tracker = self.tracker.update(detections)
        #
        # for resul2t in result_Tracker:
        #     x1, y1, x2, y2, Id = resul2t
        #     x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        #     w, h = x2 - x1, y2 - y1
        #     cvzone.cornerRect(fix_img, (x1, y1, w, h), l=7, rt=2, colorR=(255, 0, 0))
        #     cvzone.putTextRect(fix_img, f' {int(Id)}', (max(0, x1), max(35, y1 - 20)),
        #                        scale=2, thickness=3, offset=10)

        cvzone.putTextRect(fix_img, datetime.now().strftime('%y-%m-%d_%H:%M:%S'), (20, 50), scale=1, thickness=1,
                           colorT=(255, 255, 255), colorR=(0, 0, 0), font=cv2.FONT_HERSHEY_COMPLEX)

        return fix_img

    def room_mode(self, origin_image, current_time):
        """
        室內開啟人臉偵測模式
        :param image: 傳進來的原始圖片 (PerFrame）
        :return: 偵測完的圖片 (PerFrame)
        """
        fix_img = origin_image

        imgS = cv2.resize(fix_img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # 交給yolo偵測臉 並交給face_recognition偵測判斷人臉
        facePerFrame = self.model_faceDetectOnly(imgS, stream=True)

        # 傳入np array(x1,y1,x2,y2,score) 回傳ID number與np array
        detections = np.empty((0, 5))

        perFrameDetect_Face_loc = []

        # Objects boxes and ids
        objects_bbs_ids_face = []
        abandoned_object_face = []

        for r in facePerFrame:
            boxes = r.boxes
            for box in boxes:
                # 取得座標
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                # w, h = x2 - x1, y2 - y1

                perFrameDetect_Face_loc.append((y1, x2, y2, x1))
                # 這邊以下是Tracking
                # conf = math.ceil((box.conf[0] * 100)) / 100
                #currentArray = np.array([x1 * 4, y1 * 4, x2 * 4, y2 * 4, conf])
                #detections = np.vstack((detections, currentArray))

        # result_Tracker = self.tracker.update(detections)
        #
        # for resul2t in result_Tracker:
        #     x1, y1, x2, y2, Id = resul2t
        #     x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        #     w, h = x2 - x1, y2 - y1
        #     cvzone.cornerRect(fix_img, (x1, y1, w, h), l=7, rt=2, colorR=(255, 0, 0))
        #     cvzone.putTextRect(fix_img, f' {int(Id)}', (max(0, x1), max(35, y1 - 20)),
        #                        scale=2, thickness=3, offset=10)

        # 找出後 在已經縮小的畫面中找出臉在哪裡並將其encoding
        encodeCurFrame = face_recognition.face_encodings(imgS, perFrameDetect_Face_loc)

        for encoFaceFrame, faceLoc in zip(encodeCurFrame, perFrameDetect_Face_loc):
            '''
            matches將會把已經儲存起來的臉照片與現在webcam中的臉進行比對
            matches 會回傳boolean list包含所有目前照片是否相向 true代表是
            faceDis 回傳double list 越小代表越像
            '''

            if encodeCurFrame:
                matches = face_recognition.compare_faces(self.existFaceEncoding, encoFaceFrame, 0.4)
                print("Matches :", matches)
                faceDis = face_recognition.face_distance(self.existFaceEncoding, encoFaceFrame)
                #print("FaceDis :", faceDis)

                # 找出最小distance
                matcheIndex = np.argmin(faceDis)

                if matches[matcheIndex]:
                    name = self.existfaceName[matcheIndex]
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = x1, y1, x2 - x1, y2 - y1
                else:
                    name = "SUS"
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    w, h = x2 - x1, y2 - y1
                    bbox = x1, y1, x2 - x1, y2 - y1

                    # 中心點
                    cx = (x1 + x1 + w) / 2
                    cy = (y1 + y1 + h) / 2

                    # 檢查物體是否已經被檢測到
                    same_object_detected = False
                    for id, pt in self.center_points_face.items():
                        # update the center point
                        print(f'center_points.items id {id} pt {pt}')
                        self.center_points_face[id] = (cx, cy)

                        objects_bbs_ids_face.append([x1, y1, w, h, id])
                        same_object_detected = True

                        #   Add same object to the abandoned_temp dictionary. if the object is
                        #   still in the temp dictionary for certain threshold count then
                        #   the object will be considered as abandoned object
                        if id in self.abandoned_temp_face:
                            # if self.abandoned_temp[id] > 100:
                            if (datetime.now() - self.abandoned_temp_face[id]).seconds > self.susLimitTime_face:
                                abandoned_object_face.append([id, x1, y1, w, h])
                            else:
                                # Increase count for the object
                                # self.abandoned_temp[id] += 1
                                print(
                                    f'now the object has exist for: {(datetime.now() - self.abandoned_temp_face[id]).seconds} seconds')
                        break

                    if same_object_detected is False:
                        self.center_points_face[self.SUSFace_id_count] = (cx, cy)
                        self.abandoned_temp_face[self.SUSFace_id_count] = current_time
                        objects_bbs_ids_face.append([x1, y1, w, h, self.SUSFace_id_count])
                        self.SUSFace_id_count += 1

                # Clean the dictionary by center points to remove IDS not used anymore
                new_center_points = {}
                abandoned_temp_2 = {}

                for obj_bb_id in objects_bbs_ids_face:
                    print(f'now obj__bb_id is {obj_bb_id}')
                    _, _, _, _, object_id = obj_bb_id
                    center = self.center_points_face[object_id]

                    new_center_points[object_id] = center

                    if object_id in self.abandoned_temp_face:
                        temp_time = self.abandoned_temp_face[object_id]
                        abandoned_temp_2[object_id] = temp_time

                print(f'now new_center_points is {new_center_points}')
                print(f'now ab is {abandoned_temp_2}')
                # Update dictionary with IDs not used removed
                self.center_points_face = new_center_points.copy()
                self.abandoned_temp_face = abandoned_temp_2.copy()

                fix_img = cvzone.cornerRect(fix_img, bbox, rt=0)
                cvzone.putTextRect(fix_img, f'{name}', (x1 - 50, y1 - 50))

        cvzone.putTextRect(fix_img, datetime.now().strftime('%y-%m-%d_%H:%M:%S'), (20, 50), scale=1,
                           thickness=1,
                           colorT=(255, 255, 255), colorR=(0, 0, 0), font=cv2.FONT_HERSHEY_COMPLEX)

        return fix_img, abandoned_object_face

    def room_mode_goOutside(self, origin_image, current_time):
        """
        室內外出模式，一樣照家裡，只要物品一動就會有警報
        :param image: 傳進來的原始圖片 (PerFrame）
        :return: 偵測完的圖片 (PerFrame)
        """

        # Objects boxes and ids
        objects_bbs_ids = []
        abandoned_object = []

        fix_img = origin_image
        perFrame = self.model_PersonDetectOnly(origin_image, stream=True)

        # 傳入np array(x1,y1,x2,y2,score) 回傳ID number與np array
        detections = np.empty((0, 5))
        name = ''
        for frame in perFrame:
            boxes = frame.boxes
            for box in boxes:
                # 取得座標
                x1, y1, x2, y2 = box.xyxy[0]

                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                conf = math.ceil((box.conf[0] * 100)) / 100

                # 取得classID
                classId = int(box.cls[0])

                currentClass = self.classNames_PersonDetectOnly[classId]

                # print(currentClass, conf)
                if (currentClass in self.newclass) and conf > 0.35:
                    name = currentClass
                    currentArray = np.array([x1, y1, x2, y2, conf])
                    detections = np.vstack((detections, currentArray))

        result_Tracker = self.tracker.update(detections)

        for resul2t in result_Tracker:
            x1, y1, x2, y2, Id = resul2t
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            cvzone.cornerRect(fix_img, (x1, y1, w, h), l=7, rt=2, colorR=(255, 0, 0))
            cvzone.putTextRect(fix_img, f'{name} ID:{int(Id)}', (max(0, x1), max(35, y1 - 20)),
                               scale=2, thickness=3, offset=10)

            # 中心點
            cx = (x1 + x1 + w) / 2
            cy = (y1 + y1 + h) / 2

            # 檢查物體是否已經被檢測到
            same_object_detected = False
            for id, pt in self.center_points_moved.items():
                if id == Id:
                    distance = math.hypot(cx - pt[0], cy - pt[1])

                    # update the center point
                    self.center_points_moved[id] = (cx, cy)

                    objects_bbs_ids.append([x1, y1, w, h, id])
                    same_object_detected = True

                    #   Add same object to the abandoned_temp dictionary. if the object is
                    #   still in the temp dictionary for certain threshold count then
                    #   the object will be considered as abandoned object
                    if id in self.moved_temp:
                        # if self.abandoned_temp[id] > 100:
                        # if (datetime.now() - self.moved_temp[id]).seconds > self.susLimitTime:
                        #     abandoned_object.append([id, x1, y1, w, h])
                        if distance > 50:
                            abandoned_object.append([id, x1, y1, w, h])
                        # else:
                        # Increase count for the object
                        # self.abandoned_temp[id] += 1
                        # print(
                        #    f'now the object has exist for: {(datetime.now() - self.moved_temp[id]).seconds} seconds')
                    break

            if same_object_detected is False:
                self.center_points_moved[Id] = (cx, cy)
                # Add new object with initial count 1
                # self.abandoned_temp[Id] = 1
                self.moved_temp[Id] = current_time
                objects_bbs_ids.append([x1, y1, w, h, Id])

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        abandoned_temp_2 = {}

        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points_moved[object_id]

            new_center_points[object_id] = center

            if object_id in self.moved_temp:
                # counts = self.abandoned_temp[object_id]
                # abandoned_temp_2[object_id] = counts
                temp_time = self.moved_temp[object_id]
                abandoned_temp_2[object_id] = temp_time

        # Update dictionary with IDs not used removed
        self.center_points_moved = new_center_points.copy()
        self.moved_temp = abandoned_temp_2.copy()

        cvzone.putTextRect(fix_img, datetime.now().strftime('%y-%m-%d_%H:%M:%S'), (20, 50), scale=1, thickness=1,
                           colorT=(255, 255, 255), colorR=(0, 0, 0), font=cv2.FONT_HERSHEY_COMPLEX)

        return fix_img, abandoned_object
