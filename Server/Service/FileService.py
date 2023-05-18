import os
import cv2
import face_recognition
import datetime
import Service


def DeleteImage(path, filename):
    """
    刪除指定檔案
    :param path: 檔案路徑
    :param filename: 檔案名稱
    :return: 是否刪除成功
    """
    try:
        os.remove(os.path.join(path, filename))
    except FileNotFoundError:
        print("找不到檔案")
        return False
    return True


def loadingKnowFace():
    """
    從資料庫拿取所有已知人臉的圖片以及名字，並載入置List裡
    :return: FaceList, Names - 存放目前已知人臉的圖片檔list,  人名list
    """
    #from . import DBService as db

    db = Service.DBService
    # 存放圖片檔案的List 回傳用
    FaceList = []
    # 存放名字的List 回傳用
    Names = []

    # 從資料庫拿取所有filename
    nameList = db.getAllImageNames()
    # 從資料庫拿取所有圖片路徑
    pathList = db.getAllImagePath()

    for path, filename in zip(pathList, nameList):
        # 將圖片擋案加入到FaceList
        FaceList.append(cv2.imread(os.path.join(path, filename)))
        # 圖片名字也一起加進去
        Temp_name = filename.split('-')
        Names.append(Temp_name[0])
    return FaceList, Names

def loadingKnowAvatar():
    """
    從資料庫拿取所有已知虛擬頭像的圖片以及名字，並載入置List裡
    :return: AvatarList, Names - 虛擬頭像list,  人名list
    """
    db = Service.DBService
    # 存放圖片檔案的List 回傳用
    avatarList = []
    # 存放名字的List 回傳用
    Names = []

    # 從資料庫拿取所有filename
    nameList = db.getAllAvatarNames()
    # 從資料庫拿取所有圖片路徑
    pathlist = db.getAllAvatarPath()
    for path, filename in zip(pathlist, nameList):
        # 將圖片擋案加入到FaceList
        avatarList.append(cv2.imread(os.path.join(path, filename)))
        # 圖片名字也一起加進去
        Temp_name = filename.split('-')
        Names.append(Temp_name[0])
    return avatarList, Names

def saveImage(image, name, avatar) -> bool:
    """
    將圖片與虛擬臉部儲存至伺服器資料夾
    :param image: 人臉圖片
    :param name: 人名
    :param avatar: 虛擬頭像圖片
    :return: 是否成功
    """
    # 真人圖片影像檔名
    imageFileName = name + 'Real-' + datetime.datetime.now().strftime("%Y%m%d,%H_%M_%S") + '.png'
    # 虛擬圖片影像檔名
    avatarFileName = name + 'avatar-' + datetime.datetime.now().strftime("%Y%m%d,%H_%M_%S") + '.png'

    #真人圖片儲存
    cv2.imwrite(os.path.join(os.getcwd(), 'images', 'Faces', imageFileName), image)
    #虛擬頭像儲存
    cv2.imwrite(os.path.join(os.getcwd(), 'images', 'avatar', avatarFileName), avatar)

    # 將資料庫寫入資料庫 database service
    db = Service.DBService
    isImageSave = db.addImagePathToDatabase(os.path.join(os.getcwd(), 'images', 'avatar'),
                                            os.path.join(os.getcwd(), 'images', 'Faces'), imageFileName, avatarFileName)
    return isImageSave


def encodeFace(faceList):
    """
    將人臉編碼
    :param faceList: 存放人臉圖片檔的list
    :return: encodeList - 存放每張人臉編碼的list
    """
    encodeList = []
    for faceImg in faceList:
        img = cv2.cvtColor(faceImg, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
