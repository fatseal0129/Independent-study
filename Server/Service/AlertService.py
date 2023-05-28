import cv2
from vidgear.gears import WriteGear
import os


class AlertSUS:
    def __init__(self):
        self.writerList = {}
        self.ID = 1

    def susWriteFrame(self, frame, Start_recording_time):
        #_, x2, y2, w2, h2 = object
        writeFrame = frame
        # cv2.putText(writeFrame, "SUS", (x2, y2 - 10), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 2)
        # cv2.rectangle(writeFrame, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)
        self.writerList[Start_recording_time].write(writeFrame)

    def createWriter(self, current_time, frame):
        output_params = {"-fourcc": "mp4v", "-fps": 20}
        fix_current_time = current_time.strftime('%y-%m-%d_%H:%M:%S')

        output_vid_path = os.path.join(os.getcwd(), "Server", 'FileData', 'SUSPeople', "Video")
        output_vid_name = f'SUSVideo-{fix_current_time}.mp4'

        output_img_path = os.path.join(os.getcwd(), "Server", 'FileData', 'SUSPeople', 'Image')
        output_img_name = f'SUSImage-{fix_current_time}.png'

        print(f'create Writer id: {self.ID}, name: {output_vid_name}')
        # 新增影片Writer
        self.writerList[current_time] = WriteGear(output=os.path.join(output_vid_path, output_vid_name), **output_params)

        # 截圖
        cv2.imwrite(os.path.join(output_img_path, output_img_name), frame)

        self.ID += 1

        return {
            "id": self.ID-1,
            "current_time": fix_current_time,
            "output_vid_path": output_vid_path,
            "output_img_path": output_img_path,
            "output_vid_name": output_vid_name,
            "output_img_name": output_img_name
        }



    def cleanUp(self):
        for name, writer in self.writerList.items():
            print(f'writer cleanUP{name}')
            writer.close()

    def cleanSingle(self, current_time):
        self.writerList[current_time].close()
        self.writerList.clear()
