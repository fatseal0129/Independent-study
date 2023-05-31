# import uvicorn
#
# if __name__ == "__main__":
#     uvicorn.run("Server.Api.api_Server:app", reload=True)
#     uvicorn.run("Box.Api.api_frontend:app", reload=True)
# from Server.Service import DB
# import Server.Service.DatabaseService
# ddd = Server.Service.DatabaseService.DatabaseService()
# states = ddd.DeleteAllCamera()

import cv2

cap = cv2.VideoCapture('rtsp://Hank_MA303:ZH_MA303@172.20.10.10/stream1')

while True:
    _, frame = cap.read()

    cv2.imshow('test', frame)
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyWindow('test')
        cv2.waitKey(1)
        cap.release()
