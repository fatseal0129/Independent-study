# 防範保全-智能防盜攝影系統

此系統的目的主要是保護家庭與個人的安全，能夠實時監控家庭的安全狀態，並在發現入侵或其他安全問題時發出警報。它可以透過攝像頭，實時監控家庭的出入、動態和環境狀態，並且連接到手機上，讓使用者隨時隨地了解家庭的安全狀態，並且讓個人能夠注意到家庭周圍是否有可以人士出沒。

## 系統需求
啟動前需先確保下列需求有安裝到電腦上:
* Python - `3.10`以上
* Virtual Studio Tool - 只需勾選`C++桌面開發程式`
* ffmpeg
* CUDA與Cudnn (選擇性，可增加運算速度，nvidia顯卡建議裝)

接著用Python建立一個新虛擬環境，並開啟Terminal到`ProjectReal`資料夾中，輸入指令安裝所需Package
```
pip install -r requirements.txt
```
</br>

>### 安裝有問題？
>大部分問題會出在dlib中，若在安裝dlib時有問題可以嘗試去Pypi下載dlib原檔，解壓縮後將資料夾放到環境的`lib/site-packages`裡面，再開啟Terminal到資料夾中輸入以下指令安裝:
>```
>python setup.py install —no DLIB_GIF_SUPPORT
>```
</br>

## 啟動
分別開啟三個Terminal並切換你所建立的環境，三個Terminal分別用途：
1. SimpleRtspServer
2. Server端
3. Box端

</br>

### !接下來動作必須照著順序做！

</br>

### SimpleRtspServer
進入到`mediamtx`資料夾(選擇你的作業系統進入)中輸入指令開啟rtspServer：
```
./mediamtx
```
這樣就完成了！

### Server端
直接使用執行以下指令開啟Server:
```
python StartServer.py
```
等到出現ip與port資訊時，代表啟動完成！

### Box端
直接使用執行以下指令開啟Box:
```
python BoxStart.py
```

等到Box與Server連上時，代表啟動完成！

接著就能使用SwaggerAPI或是前端畫面操作了，若想開啟SwaggerAPI，只需要在Server或是Box中顯示的IP後面加入/docs即可開啟，範例：
```
127.0.0.1:8000/docs
```

</br>

## 使用SwaggerAPI新增攝影機
進入到訊號Box的Swagger，看到`/camera/add`即可加入攝影機資訊。(webcam可輸入0開啟)

格式為：
```
{
    name: "{攝影機名字}",
    url: "{網址}",
    mode: "{模式}"
}
```

模式分為：
* room - 室內模式
* outdoor - 戶外模式
* room_outside - 夜沒歸模式
* normal - 普通模式

若輸入模式是錯誤的會默認以「普通模式」執行。

輸入範例(以webcam當鏡頭)：
```
{
    name: "廚房用",
    url: "0",
    mode: "room_outside"
}
```

</br>

## 觀看鏡頭
全部開啟並成功新增攝影機後，可使用VLC或支援RTSP的播放器，輸入下列網址觀看：
```
rtsp://localhost:8554/stream/{攝影機名子}
例如：
rtsp://localhost:8554/stream/webcam1
```

</br>
