# import pymongo
# import os
# import cv2
import Service.DatabaseService as DBservice
# import numpy as np
# print(os.path.join(os.getcwd(), 'Faces'))
# x = os.getcwd()
# print(x)
# os.chdir('Service')
# x = os.getcwd()
# print(x)
# os.remove('qwe')

# x = np.empty(1)
# print(x)
#
# currentArray = np.empty(1)
# x = np.vstack((x, currentArray))
# print(x)
# import datetime

db = DBservice.DatabaseService()
if db.DeleteAllSUS():
    print("YES!")
else:
    print("shit BRO")