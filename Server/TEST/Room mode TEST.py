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
Start_recording_time = 0
while True:
    img = cap.read()
    current_time = datetime.datetime.now()
    #predict, abandoned_objects = dm.outdoor_mode(img, current_time)
    predict, abandoned_objects = dm.room_mode(img, current_time)

    if len(abandoned_objects) > 0:
        if isSusTime is False:
            alert.createWriter(current_time, img)
            Start_recording_time = current_time
            isSusTime = True
    else:
        if isSusTime:
            isSusTime = False
            alert.cleanSingle(Start_recording_time)
        Start_recording_time = current_time

    for objects in abandoned_objects:
        id, x2, y2, w2, h2 = objects
        if isSusTime:
            pass
            alert.susWriteFrame(img, Start_recording_time, objects)
        cv2.putText(predict, f'FIND SUS! Recording...', (500, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (34, 34, 178),
                    lineType=cv2.LINE_AA)

    cv2.imshow("Test", predict)

    if cv2.waitKey(1) == ord('q'):
        cv2.destroyWindow('Detect_mode_Face')
        cv2.waitKey(1)
        cap.stop()
        alert.cleanUp()
        break
