from Service import CameraManager
import cv2
import time

cv2.startWindowThread()
CameraManager.createCamera(name="TEST", url=0, initial_mode="MODE")
isThis = False
while True:
    if CameraManager.getStatus("TEST"):
        CameraManager.resumeCamera("TEST")
        time.sleep(1)
        isThis = True
        break

while True:
    if isThis:
        frame = CameraManager.getCameraFrame("TEST")
        cv2.imshow("Test", frame)

    if cv2.waitKey(1) == ord('p'):
        isThis = False
        CameraManager.pauseCamera("TEST")

    if cv2.waitKey(1) == ord('s'):
        isThis = True
        CameraManager.resumeCamera("TEST")

    if cv2.waitKey(1) == ord('q'):
        CameraManager.cleanCamera("TEST")
        cv2.destroyAllWindows()
        break
