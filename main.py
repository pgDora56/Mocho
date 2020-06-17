# coding=utf-8
from copy import deepcopy
import discord
import json
import random 
import re
import sys
import time
from threading import Timer

from board_tools import Board, WhiteBoard
from execpy import ExecPy
from join_notify import JoinNotify
import talkingbox
from tamagame import TamaGame

# config.jsonの読み込み
with open("config.json", "r") as f:
    conf = json.load(f)
client = discord.Client()


async def write(msg):
    global console
    print(msg)
    if console != None: await console.send(msg)

@client.event
async def on_ready():
    global console, board, tb, tg, join_notify_list
    boardconf = conf["board_code"][conf["board"]]
    BOARD_ID = int(boardconf["id"])
    RANDOM_ID = int(boardconf["random"])

    join_notify_pair_list = conf["join_notify"]
    join_notify_list = []
    for notify_pair in join_notify_pair_list:
        watch_category, notify_ch = notify_pair
        join_notify_list.append(JoinNotify(watch_category, client.get_channel(notify_ch)))

    console = client.get_channel(conf["console"])
    tb = talkingbox.TalkingBox(console)
    tg = TamaGame(client)
    board = Board(client.get_channel(BOARD_ID),client.get_channel(RANDOM_ID))
    try:
        await write("Login Complete")
        await write("Success to connect console")
    except Exception as e:
        await write(f"Error: {str(e)}")

@client.event
async def on_message(message):
    # メッセージの受信時に呼び出される

    global client, board, tb
    msg = message.content # メッセージの内容
    if message.author.bot: # メッセージを送っているのがbotなら何もしない
        if message.author.id == 712672371596591116 and msg.startswith("あやね"):
            await message.channel.send("あやねる～～もちょだよ～～～(o・∇・o)")
        return
    if message.channel == board.channel: 
        # ボードに来たのは全部消す
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

    if not (str(message.channel) in ["もちょ"] or str(message.channel).startswith("Direct Message") or message.channel.id in conf["acceptch"]):
        # 許可されたチャンネル以外は全てDeny
        await write(f"Message Received in {message.channel} by {message.author} in {message.channel.id} -> Deny")
        return



    await write(f"Message Received in {message.channel} by {message.author} in {message.channel.id}") # 受信

    if not(board.is_owner(message.channel) or board.is_joiner(message.channel)):
        # Board参加者の個チャ以外はトーキングボットを反応させる
        if msg.startswith("もちょ、") and msg.endswith("は好き？"):
            word = msg[4:-4]
            await tb.seed_reply(message.channel, word, [("すきだよ～！！(o・∇・o)", 70), ("かぁ、普通かな(o・∇・o)",20), ("はちょっと苦手かな～(o・∇・o)",7), ("、ぜったいゆるせへん、あたいゆるせへん",3)], "%seed%%word%")
        else:
            e = ExecPy()
            if(not await e.execution(message)):
                await tb.reply(message.channel, msg)
        return

    # 以下ボードのコマンド処理

    elif str(message.channel).startswith("Direct Message"):
        # ダイレクトメッセージの処理
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

@client.event
async def on_voice_state_update(member, before, after):
    # Voiceの状況が変わったときに呼び出される
    #  チャンネル移動やミュートの解除など（ここではチャンネル移動のみ通知させている）
    befch = before.channel
    aftch = after.channel
    if befch == tg.vc or aftch == tg.vc:
        # Call TamaGame
        await tg.member_change()

    for join_notify in join_notify_list:
        await join_notify.check(member, befch, aftch)

token = conf["token"]
client.run(token)
