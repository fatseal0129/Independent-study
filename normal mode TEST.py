import cv2
#import lightweight_detectmode
from Detect import dm
import datetime
import Service.AlertService
from vidgear.gears import CamGear

# 影片用

options = {
    "CAP_PROP_FRAME_WIDTH": 1280,
    "CAP_PROP_FRAME_HEIGHT": 960
}
cap = CamGear(source=0, **options).start()

cv2.startWindowThread()

#dm = lightweight_detectmode.DetectMode()

alert = Service.AlertService.AlertSUS()
abandoned_objects = []
isSusTime = False
Start_recording_time = datetime.datetime.now()
while True:
    img = cap.read()
    current_time = datetime.datetime.now()
    # predict, abandoned_objects = dm.outdoor_mode(img, current_time)
    predict = dm.normal_mode(img)

    cv2.imshow("Test", predict)

    if cv2.waitKey(1) == ord('q'):
        cv2.destroyWindow('Detect_mode_Face')
        cv2.waitKey(1)
        cap.stop()
        # alert.cleanUp()
        break
