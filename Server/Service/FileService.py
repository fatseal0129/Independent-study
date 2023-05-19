import os
import cv2
import face_recognition
import datetime


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

## 可能思考要傳入引數之類的 而不是直接從db拿 以下皆是
def loadingKnowFace(filenameList, pathList):
    """
    將照片載入到List裡
    :param filenameList: 所有的imgfilename
    :param pathList: 所有的imgpath
    :return: FaceList 存放目前已知人臉的圖片檔list
    """
    #from . import DBService as db

    # db = Service.DBService
    # 存放圖片檔案的List 回傳用
    FaceList = []

    # 從資料庫拿取所有filename
    # nameList = db.getAllImageNames()
    # 從資料庫拿取所有圖片路徑
    # pathList = db.getAllImagePath()

    for path, filename in zip(pathList, filenameList):
        # 將圖片擋案加入到FaceList
        FaceList.append(cv2.imread(os.path.join(path, filename)))
    return FaceList

def loadingKnowAvatar(nameList, pathList):
    """
    將所有已知虛擬頭像的圖片以及名字載入到List裡
    :param nameList: 所有的avatarfilename
    :param pathList: 所有的avatarpath
    :return: AvatarList - 虛擬頭像list
    """
    avatarList = []
    for path, filename in zip(pathList, nameList):
        # 將圖片擋案加入到FaceList
        avatarList.append(cv2.imread(os.path.join(path, filename)))
    return avatarList

def saveImage(image, name, avatar):
    """
    將圖片與虛擬臉部儲存至伺服器資料夾，成功則回傳檔名與路徑List
    :param image: 人臉圖片
    :param name: 人名
    :param avatar: 虛擬頭像圖片
    :return: (imageFilename, imagePath, avatarFilename, avatarPath)
    """

    # 真人圖片影像檔名
    imageFileName = name + 'Real-' + datetime.datetime.now().strftime("%Y%m%d,%H_%M_%S") + '.png'
    # 虛擬圖片影像檔名
    avatarFileName = name + 'avatar-' + datetime.datetime.now().strftime("%Y%m%d,%H_%M_%S") + '.png'

    imagePath = os.path.join(os.path.dirname(os.getcwd()), 'FileData', 'Member', 'faces')
    avatarPath = os.path.join(os.path.dirname(os.getcwd()), 'FileData', 'Member', 'avatar')

    #真人圖片儲存
    if not(cv2.imwrite(os.path.join(imagePath, imageFileName), image)):
        raise Exception(f'真人照片檔案儲存失敗!!\nPath:{imagePath}\nfilename{imageFileName}')
    #虛擬頭像儲存
    if not(cv2.imwrite(os.path.join(avatarPath, avatarFileName), avatar)):
        raise Exception(f'虛擬頭像儲存失敗!!\nPath:{avatarPath}\nfilename{avatarFileName}')

    return [imageFileName, imagePath, avatarFileName, avatarPath]


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