import cv2
import datetime
import os
import face_recognition


def addUserFaces():
    """
    開啟鏡頭對人臉進行照相，並儲存成.png檔
    :param name: output的檔名
    """
    isaa = False
    firstTime = datetime.datetime.now()
    cap = cv2.VideoCapture(0)
    while True:
        _, img = cap.read()
        if isaa:
            passTime = (datetime.datetime.now() - firstTime).total_seconds()
            TimeCountdown = int(10 - passTime)
            cv2.putText(img, f'Success! Leaving for {TimeCountdown}...', (40, 90), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (118, 238, 0))
            if TimeCountdown <= 0:
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                cap.release()
                return True
        elif cv2.waitKey(1) == ord('g'):
            cv2.putText(img, "Saving......", (40, 90), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0))
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faceLocList = face_recognition.face_locations(imgRGB)
            print("臉的位置:", faceLocList)
            for faceLoc in faceLocList:
                y1, x2, y2, x1 = faceLoc
                The_User = img[y1:y2, x1:x2]
                filename = firstTime.strftime("%Y%m%d,%H_%M_%S") + '.png'
                # 人臉
                cv2.imwrite(os.path.join(os.getcwd(), filename), The_User)
                # # Avatar臉 (暫時)
                cv2.imwrite(os.path.join(os.getcwd(), filename), The_User)
                isaa = True
        else:
            cv2.putText(img, "Press g for photo", (40, 90), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (85, 85, 205))

        cv2.imshow('AddUserMode', img)


if __name__ == '__main__':
    addUserFaces()
