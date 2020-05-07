# coding=utf-8
import configparser, discord, sys, random, time, re, asyncio
from threading import Timer
from board_tools import Board, WhiteBoard
import talkingbot
from copy import deepcopy

# config.iniの読み込み設定
conf_ini = configparser.ConfigParser()
conf_ini.read('config.ini', encoding='utf-8')
if conf_ini == None:
    print("Not found 'config.ini'")
    exit()
conf_mocho = conf_ini["Mocho"]
accept_ch = list(map(int, conf_mocho["AcceptCh"].split(",")))
vc_category = int(conf_mocho["VCCategory"])

debug_mode = False
board_debug = True

client = discord.Client()
mainchannel = None

async def write(msg):
    global console
    print(msg)
    if console != None: await console.send(msg)

class FileOperation:
    def __init__(self, which = 0):
        self.filename = ".bob.txt"
        if which == 1: 
            self.filename = ".codename.txt"
        elif which == 99:
            self.filename = ".codename-cand.txt"
        

    def read(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            dic = f.readlines()
        ndic = []
        for d in dic:
            ndic.append(d.strip())
        return ndic

    def add(self, word):
        be = self.read()
        if word in be:
            return False
        be.append(word)
        with open(self.filename, 'w', encoding="utf-8") as f:
            f.write('\n'.join(be))
        return True

## 以下クライアントの処理関数
@client.event
async def on_ready():
    global console, board, tb, mocho_ch
    boardconf = conf_ini[conf_mocho["Board"]]
    BOARD_ID = int(boardconf["ID"])
    RANDOM_ID = int(boardconf["RANDOM"])
    console = client.get_channel(int(conf_mocho["Console"]))
    mocho_ch = client.get_channel(int(conf_mocho["MochoCh"]))
    tb = talkingbot.Talking(console)
    board = Board(client.get_channel(BOARD_ID),client.get_channel(RANDOM_ID))
    try:
        await write("Login Complete")
        print(console)
        await write("Success to connect console")
    except Exception as e:
        await write(f"Error: {str(e)}")

@client.event
async def on_message(message):
    global fop, client, prevword, parent, mainchannel, score, cwords, cok, cdobon, cdisp, ccolor, clist, ccolor_ans, candop, board, tb
    msg = message.content
    if message.author.bot: return
    if message.channel == board.channel:
        await message.delete()
        return

    if message.channel == console:
        # Owner Command
        if msg.startswith("ADD:"):
            try:
                fname, sentences = msg[4:].split("|")
                tb.append_line(fname, sentences)
                await write(f"Success append line to {fname}")
            except:
                await write(f"Error: {msg}")
        elif msg[0] == "@":
            try:
                trigger, word = msg[1:].split("|")
                tb.next_only_word.append((trigger, word))
                await write(f"Next '{trigger}' => {word}")
            except:
                await write(f"Error: {msg}")

        await message.delete()
        await write(f"Get command {msg}")
        if msg == "~bye":
            await message.channel.send("Good bye!")
            await client.logout()
            await write("Logout Complete")
        return

    if not (str(message.channel) in ["もちょ"] or str(message.channel).startswith("Direct Message") or message.channel.id in accept_ch):
        # 許可されたチャンネル以外は全てDeny
        await write(f"Message Received in {message.channel} by {message.author} in {message.channel.id} -> Deny")
        return



    await write(f"Message Received in {message.channel} by {message.author} in {message.channel.id}")
    if not(board.is_owner(message.channel) or board.is_joiner(message.channel)):
        # Board参加者以外はトーキングボットを反応させる
        await tb.reply(message.channel, msg)

    # 以下コマンド処理

    elif str(message.channel).startswith("Direct Message"):
        # ダイレクトメッセージの処理

        # ボード
        if msg =="get board owner":
            if message.channel in board.joiner:
                await message.channel.send(f"あなたは現在参加者です。オーナーになるためには `board exit` で一旦参加者から抜けてください。")
            elif board.owner != None:
                await message.channel.send(f"現在のボードオーナーは{str(board.owner)[20:]}になっています。 `release board owner` で本人にリリースをお願いするか、Doraまでご連絡ください。")
            else:
                board.owner = message.channel
                await write(f"Set board owner: {str(board.owner)}")
                await message.channel.send(f"ボードオーナーになりました。オーナーを離れるときは `release board owner` と送ってください。")
                if len(board.joiner) == 0:
                    await message.channel.send("現在の参加者はいません")
                else:
                    await board.joiner_notify()
        elif msg == "release board owner":
            if board.owner == message.channel:
                board.owner = None
                await write(f"Release board owner: {str(board.owner)}")
                await message.channel.send(f"ボードオーナーを離れました。")
            else:
                await message.channel.send(f"あなたはボードオーナーではありません。")
        
        elif msg == "board join":
            await board.join(message.channel)
        elif msg == "board exit":
            await board.exit(message.channel)
        elif board.is_owner(message.channel):
            if msg == "reset":
                await board.reset_correct()
            elif msg == "lock":
                await board.lock()
            elif msg == "next":
                await board.next()
            elif msg == "info":
                await board.send_info()
            elif msg == "score":
                await board.send_rank(board.owner)
            elif msg.startswith("open:"):
                await board.open(msg[5:])
            elif msg.startswith("c"):
                await board.correct_check_by_id(msg[1:])
            elif msg[0].isdecimal() and msg.count("=") == 1:
                try:
                    pl, sc = msg.split("=")
                    board.joiner[int(pl)].score = int(sc)
                    await message.channel.send(f"Scoreを変更しました")
                    await board.send_rank(board.owner)
                except Exception as ex:
                    await message.channel.send(f"Scoreの変更に失敗しました：{str(ex)}")
        elif board.is_joiner(message.channel):
            await board.joiner_write(message.channel, msg)


        # ボードここまで

@client.event
async def on_voice_state_update(member, before, after):
    befch = before.channel
    aftch = after.channel
    send = False
    if befch == None:
        if aftch.category_id == vc_category:
            msg = await mocho_ch.send(f"{member.display_name}が `{aftch}` に入室したよ(o・∇・o)")
            send = True
    elif aftch == None:
        if befch.category_id == vc_category:
            msg = await mocho_ch.send(f"{member.display_name}が `{befch}` から退出したよ(o・∇・o)")
            send = True
    elif befch != aftch:
        if before.channel.category_id == vc_category or after.channel.category_id == vc_category:
            msg = await mocho_ch.send(f"{member.display_name}が `{befch}` から `{aftch}` に移動したよ(o・∇・o)")
            send = True

    if send:
        await asyncio.sleep(180)
        await msg.delete()
    print(member.display_name)
        

token = conf_ini.get("Mocho", "Token")
fop = FileOperation(0)
cfop = FileOperation(1)
candop = FileOperation(99)
client.run(token)
