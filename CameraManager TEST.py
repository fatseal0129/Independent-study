from Service import CameraManager
import cv2
import time

cv2.startWindowThread()
CameraManager.createCamera(name="TEST", url=0, initial_mode="MODE")
