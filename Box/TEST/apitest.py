import requests
import cv2
import io
import numpy as np
from PIL import Image
import base64

raw_face = cv2.imread('Face-Zhuming.png')

_, face_buffer = cv2.imencode('.jpg', raw_face)

str_face = base64.b64encode(face_buffer).decode('utf-8')

raw_faceavatar = cv2.imread('Avatar-Zhuming.png')

_, avatar_buffer = cv2.imencode('.jpg', raw_faceavatar)

str_avatar = base64.b64encode(avatar_buffer).decode('utf-8')



## decode
#
# face_original = base64.b64decode(str_face)
# face_as_np = np.frombuffer(face_original, dtype=np.uint8)
# image_buffer = cv2.imdecode(face_as_np, flags=1)



# #
# cv2.imshow('My Image', image_buffer)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#
# data = {
#             "name": 'Zhuming',
#             'image': str_face,
#             'avatar': str_avatar,
# }
#
# r = requests.post(url="http://127.0.0.1:8000/member/add", json=data)
# if r.status_code == 200:
#     print(f'伺服器回傳: {r.text}')
#     print(f'{r.content}')
# else:
#     print(f'加入失敗！statusCode:{r.status_code}\nReason:{r.reason}')