# coding=utf-8
import configparser
import discord
import json
import pickle
import time

with open("config.json", "r") as f:
    conf = json.load(f)
tg_zatsu_id = conf["tamagame"]


class TamaGame:
    def __init__(self, client):
        self.zatsudan = client.get_channel(tg_zatsu_id)
        self.vc = client.get_channel(tg_zatsu_id + 1)
        try:
            with open("pickles/tamagame.pickle", "rb") as f:
                lis = pickle.load(f)
            self.talking_num = lis[0]
            self.talkstart = lis[1]
            self.sendpng = lis[2]
            self.member_change()
        except: 
            self.talking_num = len(self.vc.members)
            self.talkstart = -1
            self.sendpng = None

    async def chat(self, msg):
        await self.zatsudan.send(msg)

    async def member_change(self):
        newnum = get_vc_members()
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
                time_str = f"{int(h)}時間" if h > 0 else ""
                time_str += f"{int(m)}分{int(sec)}秒"
                await self.chat(f"お疲れ様！{time_str}喋ってたよ！(o・∇・o)")
                self.talkstart = -1
        else:
            self.sendpng = None

        self.talking_num = newnum
        self.record()

    def get_vc_members(self):
        human_user_cnt = 0
        for m in self.vc.members:
            if not m.bot: human_user_cnt += 1
        print(f"Human: {human_user_cnt}")
        return human_user_cnt


    def record(self):
        with open("pickles/tamagame.pickle", "wb") as f:
            pickle.dump(list([self.talking_num, self.talkstart, self.sendpng]), f)

