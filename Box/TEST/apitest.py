# import the necessary packages
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import time
import cv2
import uvicorn
from multiprocessing import Process, Queue


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = None

def start_stream(url_rtsp, manager):
    cap = cv2.VideoCapture(url_rtsp)
    while True:
        _, frame = cap.read()
        _, encoded = cv2.imencode('.jpg', frame)
        manager.put(encoded)
        time.sleep(0.2)


def streamer():
    try:
        while manager:
            frame = manager.get()
            print(frame)
            yield b'data:'+frame.tobytes()+b'\n\n'
            # yield b'--frame\r\n' + frame.tobytes() + b'\r\n'
            # yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            #        frame.tobytes() + b'\r\n')
    except GeneratorExit:
        print("cancelled")

@app.get("/getVideo")
async def video_feed():
    return StreamingResponse(streamer(), media_type='text/event-stream')

@app.get("/keep-alive")
def keep_alive():
    global manager
    if not manager:
        manager = Queue()
        p = Process(target=start_stream, args=(0, manager,))
        p.start()
        return "YES!"

if __name__ == "__main__":
    uvicorn.run("apitest:app", reload=True)