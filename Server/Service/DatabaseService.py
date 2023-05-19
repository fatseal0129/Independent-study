# 與資料庫相關的功能
# 1. 新增一筆資料
# 2. 查詢資料
# 3. 更新資料
# 4. 刪除資料
# 5. 建立資料庫
# 6. 取得所有資料
# 7. 取得所有資料的網址
# 8. 新增一筆資料的網址
# 9. 更新一筆資料的網址

# connect to mongoDB
import pymongo
from Server.Service import FileManager

class DatabaseService:
    def __init__(self):
        # 連接到mongoDB
        self.mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")

        # 新增一個database 名稱為 CamDB，若已存在則是指向的意思
        self.camDB = self.mongoclient["CamDB"]

        # 新增一個collection，名稱為Member，用來存放圖片網址，若已存在則是指向的意思
        self.col_Member = self.camDB["Member"]

        # 新增一個collection，名稱為Amogus，用來存放可疑人士，若已存在則是指向的意思
        self.col_Amogus = self.camDB["Amogus"]

    def addMemberToDatabase(self, name: str, imgfilename: str, avatarfilename: str,
                            avatarpath: str, imagepath: str) -> bool:
        """
        新增人/虛擬頭像的圖片資料(路徑與名字)到database
        :param avatarpath: 存放虛擬頭像的路徑
        :param imagepath: 存放人臉圖片的路徑
        :param name: 人名
        :param avatarfilename: 虛擬頭像檔名
        :param imgfilename: 真實人臉檔名
        :return: 是否新增成功

        """
        data = {"name": name,
                "imgfilename": imgfilename,
                "avatarfilename": avatarfilename,
                "avatarpath": avatarpath,
                "imagepath": imagepath}

        result = self.col_Member.insert_one(data)
        print("新增完顯示結果：", result.acknowledged)
        return result.acknowledged

    def addAmogus(self, Id:int, currentTime, videoPath:str = "", imagePath:str = "",
                  vidFilename:str = "", imgFilename:str= "") -> bool:
        """
        新增可疑人士
        :param Id: ID
        :param currentTime: 出現時間
        :param videoPath: 影片路徑
        :param imagePath: 圖片路徑
        :param vidFilename: 影片檔名
        :param imgFilename: 圖片
        :return:
        """
        data = {
            "id": Id,
            "appear": currentTime,
            "imagePath": imagePath,
            "videoPath": videoPath,
            "vidFilename": vidFilename,
            "imgFilename": imgFilename
        }
        result = self.col_Amogus.insert_one(data)
        print("新增完顯示結果：", result.acknowledged)
        return result.acknowledged

    def getAllSUS(self):
        """
        取得所有可疑人士
        :return:
        """
        imposter = []
        for sus in self.col_Amogus.find():
            imposter.append(sus)
        return imposter

    def getAllMemberData(self):
        """
        取得所有家庭成員資料
        :return:
        """
        data = []
        for person in self.col_Member.find():
            data.append(person)
        return data

    def getMemberAvatarPath(self, name: str = ''):
        """
        取得單一頭像圖片的路徑
        :param name: 名字
        :return: 路徑，若沒有則回傳空字串
        """
        path = self.col_Member.find_one({"name": {"$regex": name}})
        if path is None:
            return ''
        else:
            return path['avatarpath']

    def getSUSImagePath(self, current_time):
        """
        取得單一SUS截圖的路徑
        :param current_time: 節錄時間
        :return: 路徑，若沒有則回傳空字串
        """
        sus = self.col_Amogus.find_one({"appear": {"$regex": current_time}})
        if sus is None:
            return ''
        else:
            return sus['imagePath']

    def getSUSVideoPath(self, current_time):
        """
        取得單一SUS影片的路徑
        :param current_time: 節錄時間
        :return: 路徑，若沒有則回傳空字串
        """
        sus = self.col_Amogus.find_one({"appear": {"$regex": current_time}})
        if sus is None:
            return ''
        else:
            return sus['videoPath']

    def getMemberImagePath(self, name: str = ''):
        """
        取得單一人臉圖片的路徑
        :param name: image名字
        :return: 路徑，若沒有則回傳空字串
        """
        path = self.col_Member.find_one({"name": {"$regex": name}})
        if path is None:
            return ''
        else:
            return path['imagepath']

    def getAllAvatarPath(self):
        """
        取得所有虛擬頭像的路徑
        :return: 存放所有虛擬圖片路徑的List
        """
        paths = []
        for path in self.col_Member.find():
            paths.append(path['avatarpath'])
        return paths

    def getAllMemberImagePath(self):
        """
        取得所有人臉圖片的路徑
        :return: 存放所有人臉圖片路徑的List
        """
        paths = []
        for path in self.col_Member.find():
            paths.append(path['imagepath'])
        return paths

    def getAllMemberNames(self):
        """
        取得所有成員人名
        :return: 存放所有人名的List
        """
        names = []
        for name in self.col_Member.find():
            names.append(name['name'])
        return names

    def getAllSUSImagePath(self):
        """
        取得所有懷疑人圖片路徑
        :return: 存放所有SUS人圖片路徑的List
        """
        sus = []
        for path in self.col_Amogus.find():
            sus.append(path['imagePath'])
        return sus

    def getAllSUSVideoPath(self):
        """
        取得所有懷疑人影片路徑
        :return: 存放所有SUS人影片路徑的List
        """
        sus = []
        for path in self.col_Amogus.find():
            sus.append(path['videoPath'])
        return sus

    def getAllMemberImageFileNames(self):
        """
        取得所有人臉照片的檔名
        :return: 存放所有檔名的List
        """
        names = []
        for name in self.col_Member.find():
            names.append(name['imgfilename'])
        return names

    def getAllMemberAvatarFileNames(self):
        """
        取得所有虛擬頭像照片的檔名
        :return: 存放所有頭像檔名的List
        """
        names = []
        for name in self.col_Member.find():
            names.append(name['avatarfilename'])
        return names

    def getAllSUSVideoNames(self):
        """
        取得所有SUS人影片的檔名
        :return: 存放所有SUS人影片的List
        """
        names = []
        for name in self.col_Amogus.find():
            names.append(name['vidFilename'])
        return names

    def getAllSUSImageNames(self):
        """
        取得所有SUS人圖片的檔名
        :return: 存放所有SUS人圖片的List
        """
        names = []
        for name in self.col_Amogus.find():
            names.append(name['imgFilename'])
        return names

    def getMemberImageFileName(self, name):
        """
        取得單一人臉檔案名稱
        :param name: image檔名
        :return: 檔案名稱
        """
        filename = self.col_Member.find_one({"name": {"$regex": name}})
        if filename is None:
            return ''
        else:
            return filename['imgfilename']

    def getMemberAvatarFileName(self, name):
        """
        取得單一虛擬頭像檔案名稱
        :param name: avatar檔名
        :return: 檔案名稱
        """
        filename = self.col_Member.find_one({"name": {"$regex": name}})
        if filename is None:
            return ''
        else:
            return filename['avatarfilename']

    def getSUSVideoName(self, current_time):
        """
        取得單一SUS影片的檔名
        :param current_time: 節錄時間
        :return: 路徑，若沒有則回傳空字串
        """
        sus = self.col_Amogus.find_one({"appear": {"$regex": current_time}})
        if sus is None:
            return ''
        else:
            return sus['vidFilename']

    def getSUSImageName(self, current_time):
        """
        取得單一SUS截圖的檔名
        :param current_time: 節錄時間
        :return: 路徑，若沒有則回傳空字串
        """
        sus = self.col_Amogus.find_one({"appear": {"$regex": current_time}})
        if sus is None:
            return ''
        else:
            return sus['imgFilename']

    def DeleteMember(self, name=''):
        """
        刪除單一人的人臉圖片與虛擬頭像資料
        :param name: 使用者名
        :return: 是否刪除成功，找不到資料也會回傳False
        """
        if self.getMemberImageFileName(name) == '':
            print("刪除失敗！原因：查無資料")
            return False
        else:
            ImagePath = self.getMemberImagePath(name)
            avatarPath = self.getMemberAvatarPath(name)
            imageFilename = self.getMemberImageFileName(name)
            avatarFilename = self.getMemberAvatarFileName(name)

            if FileManager.DeleteImage(ImagePath, imageFilename) and \
                    FileManager.DeleteImage(avatarPath, avatarFilename):
                x = self.col_Member.delete_one({"name": {"$regex": name}})
                print("刪除成功！")
                print(x.deleted_count, "筆資料被刪除")
                return True
            else:
                print("刪除失敗！ 找不到檔案")
                return False

    def DeleteSUS_time(self, current_time):
        """
        刪除單一SUS人的資料 使用current_time
        :param current_time: 節錄時間
        :return: 是否刪除成功，找不到資料也會回傳False
        """
        if self.getSUSImageName(current_time) == '':
            print("刪除失敗！原因：查無資料")
            return False
        else:
            vidPath = self.getSUSVideoPath(current_time)
            vidFilename = self.getSUSVideoName(current_time)

            imgPath = self.getSUSImagePath(current_time)
            imgFilename = self.getSUSImageName(current_time)

            if FileManager.DeleteImage(vidPath, vidFilename) and FileManager.DeleteImage(imgPath, imgFilename):
                result = self.col_Amogus.delete_one({"appear": {"$regex": current_time}})
                print("刪除成功！")
                print(result.deleted_count, "筆資料被刪除")
                return True
            else:
                print("刪除失敗！ 找不到檔案")
                return False

    def DeleteAllSUS(self):
        """
        刪除所有可疑人士圖片資料
        :return: 是否刪除成功
        """
        i = 0
        vidPath = self.getAllSUSVideoPath()
        vidFilename = self.getAllSUSVideoNames()

        imgPath = self.getAllSUSImagePath()
        imgFilename = self.getAllSUSImageNames()

        for vpath, vfile, ipath, ifile in zip(vidPath, vidFilename, imgPath, imgFilename):
            if FileManager.DeleteImage(vpath, vfile) and FileManager.DeleteImage(ipath, ifile):
                if self.col_Amogus.delete_one({"vidFilename": {"$regex": vfile}}):
                    print("刪除成功！")
                    i += 1
                else:
                    print(f'失敗！ 找不到資料庫資料！{vfile}')
                    return False
            else:
                print(f'失敗！ 找不到檔案！{vfile} 或{ifile}')
                return False

        print(f'{i}筆資料被刪除')
        return True

    def DeleteAllMember(self):
        """
        刪除所有圖片資料
        :return: 是否刪除成功
        """
        x = self.col_Member.delete_many({})
        print("刪除成功！")
        print(x.deleted_count, "筆資料被刪除")
        return True

    def updateMember(self):
        pass

# # 更新資料
# myquery = {"name": "John"}
# newvalues = {"$set": {"address": "Canyon 123"}}

#
# # Update data in MongoDB
# collection.update_one({"name": "John"}, {"$set": {"address": "Canyon 123"}})
#
# # Delete collection in MongoDB
# collection.drop()
#
# # Delete database in MongoDB
# client.drop_database("Face_Recognition")
#
# # Close MongoDB connection
# client.close()
#
# # Query all data in MongoDB
# for x in collection.find():
#     print(x)
#
# # Query data with condition in MongoDB
# for x in collection.find({"name": "John"}):
#     print(x)
#
# # Query data with condition in MongoDB
# for x in collection.find({"name": {"$gt": "H"}}):
#     print(x)

# # Query data with condition in MongoDB
# for x in collection.find({"name": {"$regex": "^J"}}):
#     print(x)
