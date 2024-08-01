import requests
import random
import urllib
import time
import json
import websocket
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
    async def __init__(self, roomname, pw, dchannel):
        websocket.enableTrace(False)
        self.tryCount = -1
        self.joinedRoom = -1
        self.status = "lobby"  # lobby, waiting
        self.roomname = roomname
        self.pw = pw
        self.channel = dchannel
        self.rooms = []
        self.message_stock = []
    
    async def run(self):
        await self.send_loop()
         
        YQUI_WS_URI = "ws://yqui.net/ws"
        self.ws = websocket.WebSocketApp(YQUI_WS_URI,
            on_message = lambda ws, msg: self.on_message(ws, msg),
            on_error   = lambda ws, msg: self.on_error(ws, msg),
            on_close   = lambda ws: self.on_close(ws))
        self.ws.on_open = lambda ws: self.on_open(ws)
        self.ws.run_forever()

    # FIXME: Discord送信がうまくいかない足掻き
    async def send_loop(self):
        while True:
            if len(self.message_stock) > 0:
                msg = self.message_stock.pop(0)
                await self.channel.send(msg)
            await asyncio.sleep(0.1)

    def send_to_channel(self, msg):
        if self.channel == None:
            print("Send: " + msg)
        else:
            self.message_stock.append(msg)
    
    def on_message(self, ws, message):
        msg = json.loads(message)
        print(msg)
        if "type" in msg:
            if msg["type"] == "rooms":
                self.rooms = msg["content"]
                if self.tryCount == -1:
                    self.tryCount = 0
                    self.try_to_create_room()
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
                    self.ws.close()


    # エラー時に呼ばれる関数
    def on_error(self, ws, error):
        self.send_to_channel("Error: " + error)
        # self.ws.close()

    # サーバーから切断時に呼ばれる関数
    def on_close(self, ws):
        # print("### closed ###")
        pass

    # サーバーから接続時に呼ばれる関数
    def on_open(self, ws):
        thread.start_new_thread(self.run, ())

    # サーバーから接続時にスレッドで起動する関数
    def run(self, *args):
        pass
        # time.sleep(5)
        # while True:
        #     self.try_to_create_room()
        #     time.sleep(30)
    
        # self.ws.close()
        # print("thread terminating...")
    
    def try_loop(self):
        while True:
            if self.status != "lobby":
                return 
            if self.tryCount > 120:
                self.send_to_channel("Failed to open room")
                self.ws.close()
                return
            self.try_to_create_room()
            time.sleep(30)
    
    def try_to_create_room(self):
        tryOpen = -1
        for room in self.rooms:
            if room["numUsers"] == 0:
                tryOpen = room["no"]
                break
        if tryOpen == -1:
            self.send_to_channel("No room available")
            return None
        self.tryCount += 1

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




if __name__ == '__main__':
    # NagayaOpener.openroom("Test", "test")
    YOpener("QAS", "qas", None).run_forever()