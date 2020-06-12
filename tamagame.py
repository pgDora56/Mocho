# coding=utf-8
import configparser
import time
import discord

# config.iniの読み込み設定
conf_ini = configparser.ConfigParser()
conf_ini.read('config.ini', encoding='utf-8')
if conf_ini == None:
    print("Not found 'config.ini'")
    exit()
tg_zatsu_id = int(conf_ini["TamaGame"]["ZATSUDAN"])


class TamaGame:
    def __init__(self, client):
        self.zatsudan = client.get_channel(tg_zatsu_id)
        self.vc = client.get_channel(tg_zatsu_id + 1)
        self.talking_num = len(self.vc.members)
        self.talkstart = -1
        self.sendpng = None

    async def chat(self, msg):
        await self.zatsudan.send(msg)

    async def member_change(self):
        newnum = len(self.vc.members)
        if self.talking_num == newnum:
            return
        if self.talking_num == 0 and newnum == 1:
            self.talkstart = time.time()
            print("Talk start")
            self.sendpng = await self.zatsudan.send(file=discord.File("tsuwa_in.png"))
        elif self.talking_num == 1 and newnum == 0:
            if self.talkstart == -1:
                print("Time End Error")
            elif self.sendpng != None:
                await self.sendpng.delete()
                self.talkstart = -1
            else:
                sec = time.time() - self.talkstart
                m = sec // 60
                sec = sec % 60
                h = m // 60
                m = m % 60
                time_str = f"{h}時間" if h > 0 else ""
                time_str += f"{int(m)}分{int(sec)}秒"
                await self.chat(f"お疲れ様！{time_str}喋ってたよ！(o・∇・o)")
                self.talkstart = -1
        else:
            self.sendpng = None

        self.talking_num = newnum




