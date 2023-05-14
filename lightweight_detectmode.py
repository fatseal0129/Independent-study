import cvzone
#import Service.FileService as FileService
from ultralytics import YOLO
import math
#from cvzone.FaceMeshModule import FaceMeshDetector
from sort import *
from datetime import datetime


class DetectMode:
    def __init__(self):
        # 載入偵測「人臉」model
        # self.model_faceDetectOnly = YOLO('yolo-weights/yolov8n-face.pt')

        # 讀取偵測「人臉」model的class名稱
        # self.classNames_faceDetectOnly = self.model_faceDetectOnly.names

        # 載入偵測「人體」model
        self.model_PersonDetectOnly = YOLO('yolo-weights/yolov8n.pt')

        # 讀取偵測「人體」model的class名稱
        self.classNames_PersonDetectOnly = self.model_PersonDetectOnly.names
        # Tracking instance
        self.tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

        self.newclass = ["backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"]

        # 保留ID的 counts （counts作為偵測是否停留太久）
        # 當有新物件的id被檢測到會被賦予新的id 這個作為目前id的計數器
        # self.SUSFace_id_count = 0

        self.moved_temp = {}
        self.center_points_moved = {}

        # ID持續多久(秒)會變成可疑人物
        self.susLimitTime = 20

        # self.existFaceList, self.existfaceName = FileService.loadingKnowFace()
        # self.existFaceEncoding = FileService.encodeFace(self.existFaceList)

    def room_mode_goOutside(self, origin_image, current_time):
        """
        外出模式，一樣照家裡，只要物品一動就會有警報
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
                        #else:
                            # Increase count for the object
                            # self.abandoned_temp[id] += 1
                            #print(
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
