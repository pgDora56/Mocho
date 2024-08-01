import requests
import random
import urllib
import time
import json
import websocket
import datetime
# import threading
import asyncio
try:
    import thread
except ImportError:
    import _thread as thread
import time

with open("config.json", "r") as f:
    conf = json.load(f)
console_id = conf["console"]  # for debug


class NagayaOpener:
    def openroom(user, pw):
        roomnumbers = [str(i) for i in range(1, 9)]
        random.shuffle(roomnumbers)
        roomno = ""
        result = ""

        while result != "ok":
            if len(roomnumbers) == 0:
                return None
            roomno = roomnumbers.pop()
            url = "https://penpenpng.com/nqa2/api/create/room" + \
                roomno
            params = {
                "name": user,
                "password": pw
            }
            response = requests.post(
                url=url,
                data=urllib.parse.urlencode(params),
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            result = response.text
            print(response.status_code)
            print(response.text)
            time.sleep(1)
        return roomno

class YOpener:
    def __init__(self, roomname, pw, sender):
        websocket.enableTrace(False)
        self.tryCount = -1
        self.joinedRoom = -1
        self.status = "lobby"  # lobby, waiting
        self.roomname = roomname
        self.pw = pw
        self.channel = sender 
        self.loop = True
        self.rooms = []
    
    def start(self):
        YQUI_WS_URI = "ws://yqui.net/ws"
        self.ws = websocket.WebSocketApp(YQUI_WS_URI,
            on_message = self.on_message,
            on_error   = self.on_error,
            on_close   = self.on_close)
        self.ws.on_open = lambda ws: self.on_open(ws)
        self.ws.run_forever()
        # wsthread = threading.Thread(self.ws.run_forever)
        # wsthread.start()
        # time.sleep(30)
        # wsthread.raise_exception()

    def send_to_channel(self, msg):
        if self.channel == None:
            print("Log: " + msg)
        else:
            self.channel.send(msg)
    
    def on_message(self, ws, message):
        msg = json.loads(message)
        if "type" in msg:
            # print(msg["type"])
            if msg["type"] == "rooms":
                self.rooms = msg["content"]
                if self.tryCount == -1:
                    self.tryCount = 0
                    success = self.try_to_create_room()
                    # 以下はリトライ機能実装前の一時的なコード
                    if not success:
                        self.ws.close()
                        self.channel.close()
            if msg["type"] == "joined":
                announce = "部屋を開きました。\n\n" + \
                    f"Yqui Room{msg['content']} {self.roomname}\n" + \
                    f"パスワードは {self.pw} です。\n" + \
                    f"http://yqui.net/room/{msg['content']}"
                self.send_to_channel(announce)
                self.joinedRoom = int(msg["content"]) - 1
                self.status = "waiting"
            if msg["type"] == "sound":
                if self.rooms[self.joinedRoom]["numUsers"] > 1:
                    # 自分以外にいるっぽいので自分は抜ける
                    ws.close()
        else:
            print(msg)


    # エラー時に呼ばれる関数
    def on_error(self, ws, error):
        self.send_to_channel("Error: " + str(error))

    # サーバーから切断時に呼ばれる関数
    def on_close(self, ws, close_status_code, close_msg):
        if self.channel != None:
            self.channel.close()
            self.loop = False

    # サーバーから接続時に呼ばれる関数
    def on_open(self, ws):
        pass
    
    # def try_loop(self):
    #     print("call try_loop")
    #     while self.loop:
    #         if self.status != "lobby":
    #             return 
    #         if self.tryCount > 120:
    #             self.send_to_channel("Failed to open room")
    #             self.ws.close()
    #             return
    #         self.try_to_create_room()
    #         print("sleep 30")
    #         time.sleep(30)
    
    def try_to_create_room(self):
        tryOpen = -1
        for room in self.rooms:  # For production
        # for rno in range(2):  # For debug
        #     room = self.rooms[rno] # For debug
            if room["numUsers"] == 0:
                tryOpen = room["no"]
                break
        if tryOpen == -1:
            print("No room available")
            nowtime = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).time()
            self.send_to_channel(f"{str(nowtime)}: No room available")
            return False 
        self.tryCount += 1

        print("Try to open room")
        req = {
            "c": "join",
            "a": {
                "name": "Momo",
                "observer": True,
                "chatAnswer": False,
                "color": {
                    "index": 0, 
                    "custom": "#FFC0CB"
                },
                "roomNo": tryOpen,
                "first": True,
                "tag": {
                    "title": self.roomname,
                    "password": self.pw
                },
                "scoreBackup": None 
            }
        }
        self.ws.send(json.dumps(req))
        return True

class Sender:
    def __init__(self, channel):
        self.channel = channel
        self.message_stock = []
        self.available = True
    
    async def run(self):
        while self.available:
            if len(self.message_stock) > 0:
                msg = self.message_stock.pop(0)
                await self.channel.send(msg)
            await asyncio.sleep(1)

    def send(self, msg):
        self.message_stock.append(msg)
    
    def close(self):
        self.available = False



if __name__ == '__main__':
    # NagayaOpener.openroom("Test", "test")
    YOpener("QAS", "qas", None).run()
