import discord
import random
import string
import json
import threading

from board_tools import Board
from execpy import ExecPy
from join_notify import JoinNotify
import talkingbox
import markov
from tamagame import TamaGame
from openroom import NagayaOpener, YOpener, Sender
from trans import TransMocho

# config.jsonの読み込み
with open("config.json", "r") as f:
    conf = json.load(f)
client = discord.Client()


async def write(msg):
    global console
    print(msg)
    if console is not None:
        await console.send(msg)


@client.event
async def on_ready():
    global console, board, tb, tg, join_notify_list, trmco
    boardconf = conf["board_code"][conf["board"]]
    BOARD_ID = int(boardconf["id"])
    RANDOM_ID = int(boardconf["random"])

    join_notify_pair_list = conf["join_notify"]
    join_notify_list = []
    for notify_pair in join_notify_pair_list:
        watch_category, notify_ch = notify_pair
        join_notify_list.append(
            JoinNotify(watch_category, client.get_channel(notify_ch))
        )

    console = client.get_channel(conf["console"])
    tb = talkingbox.TalkingBox(console)
    tg = TamaGame(client)
    trmco = TransMocho(conf["deepl_token"])
    board = Board(client.get_channel(BOARD_ID), client.get_channel(RANDOM_ID))
    try:
        await write("Login Complete")
        await write("Success to connect console")
    except Exception as e:
        await write(f"Error: {str(e)}")


@client.event
async def on_message(message):
    # メッセージの受信時に呼び出される
    global conf, client, board, tb, trmco
    msg = message.content  # メッセージの内容
    if message.author.bot:  # メッセージを送っているのがbotなら何もしない
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
            except Exception:
                await write(f"Error: {msg}")
        elif msg[0] == "@":
            try:
                trigger, word = msg[1:].split("|")
                tb.next_only_word.append((trigger, word))
                await write(f"Next '{trigger}' => {word}")
            except Exception:
                await write(f"Error: {msg}")

        await message.delete()
        await write(f"Get command {msg}")
        if msg == "~bye":
            await message.channel.send("Good bye!")
            await client.logout()
            await write("Logout Complete")
        return

    if not (str(message.channel) in ["もちょ"] or
            str(message.channel).startswith("Direct Message") or
            message.channel.id in conf["acceptch"]):
        # 許可されたチャンネル以外は全てDeny
        await write(f"Message Received in {message.channel} " +
                    f"by {message.author} " +
                    f"in {message.channel.id} -> Deny")
        return

    await write(f"Message Received in {message.channel} " +
                f"by {message.author} " +
                f"in {message.channel.id}")  # 受信

    if not(board.is_owner(message.channel) or
           board.is_joiner(message.channel)):
        # Board参加者の個チャ以外はトーキングボットを反応させる
        if msg.startswith("もちょ、"):
            if msg.endswith("は好き？"):
                word = msg[4:-4]
                await tb.seed_reply(message.channel, word, [
                    ("すきだよ～！！(o・∇・o)", 70),
                    ("かぁ、普通かな(o・∇・o)", 20),
                    ("はちょっと苦手かな～(o・∇・o)", 7),
                    ("、ぜったいゆるせへん、あたいゆるせへん", 3)
                ], "%seed%%word%")
                return
            elif msg.endswith("で何？"):
                # ex:もちょ、イージオスはマレーシア語で何？
                text_lang = msg[4:-3]
                lang = ""
                text = ""
                for i in range(len(text_lang)-1, -1, -1):
                    if text_lang[i] == "は":
                        text = text_lang[:i]
                        break
                    lang = text_lang[i] + lang
                if text != "" and lang != "":
                    await message.channel.send(trmco.mocho_response(lang, text))
                    return
            elif msg.endswith("は何？"):
                # ex:もちょ、マレーシア語でイージオスは何？
                text_lang = msg[4:-3]
                lang = ""
                text = ""
                for i in range(len(text_lang)):
                    if text_lang[i] == "で":
                        text = text_lang[i+1:]
                        break
                    lang += text_lang[i]
                if text != "" and lang != "":
                    await message.channel.send(trmco.mocho_response(lang, text))
                    return
        elif msg.startswith("fakesing"):
            command = msg.split("-")
            get_items = 1
            if len(command) > 1:
                if command[1].isdigit():
                    n = int(command[1])
                    if n > 20:
                        get_items = 20
                    elif n > 0:
                        get_items = n
            await message.channel.send(markov.get_markov(conf["mecab_dic"], "sing.tb", get_items))
        elif msg.startswith("nopen"):
            command = msg.split()
            print(command)
            if len(command) == 2:
                randlst = [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
                command.append("".join(randlst))
            if len(command) == 3:
                if 0 < len(command[1]) <= 10 and \
                        0 < len(command[2]) <= 10:
                    try:
                        no = NagayaOpener.openroom(command[1], command[2])
                        if no is None:
                            return
                        announce = "部屋を開きました。\n\n" + \
                            f"Nagaya Quiz Arena2 Room{no} {command[1]}\n" + \
                            f"パスワードは {command[2]} です。\n" + \
                            f"出題者: https://penpenpng.com/nqa2/room{no}/provider\n" + \
                            f"解答者: https://penpenpng.com/nqa2/room{no}/player"
                        await message.channel.send(announce)
                        await write(f"Open room{no}\nName:{command[1]}\nPW:{command[2]}")
                    except Exception as e:
                        await write("Roomopen Error:" + str(e))
                else:
                    await message.channel.send("部屋名とパスワードは10文字以内で指定してください。")
        elif msg.startswith("yopen"):
            command = msg.split()
            print(command)
            if len(command) == 2:
                randlst = [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
                command.append("".join(randlst))
            if len(command) == 3:
                if 0 < len(command[1]) <= 20 and \
                        0 < len(command[2]) <= 20:
                    try:
                        s = Sender(message.channel)
                        y = YOpener(command[1], command[2], s)
                        y_thread = threading.Thread(target=y.start)
                        y_thread.start()
                        await s.run()
                        y_thread.join()
                    except:
                        pass  # 握りつぶして良い
                else:
                    await message.channel.send("部屋名とパスワードは20文字以内で指定してください。")
        else:
            e = ExecPy()
            if(not await e.execution(message)):
                await tb.reply(message.channel, msg)
        return

    # 以下ボードのコマンド処理

    elif str(message.channel).startswith("Direct Message"):
        # ダイレクトメッセージの処理
        if msg == "get board owner":
            if message.channel in board.joiner:
                await message.channel.send("あなたは現在参加者です。オーナーになるためには `board exit` で一旦参加者から抜けてください。")
            elif board.owner is not None:
                await message.channel.send(f"現在のボードオーナーは{str(board.owner)[20:]}になっています。 `release board owner` で本人にリリースをお願いするか、Doraまでご連絡ください。")
            else:
                board.owner = message.channel
                await write(f"Set board owner: {str(board.owner)}")
                await message.channel.send("ボードオーナーになりました。オーナーを離れるときは `release board owner` と送ってください。")
                if len(board.joiner) == 0:
                    await message.channel.send("現在の参加者はいません")
                else:
                    await board.joiner_notify()
        elif msg == "release board owner":
            if board.owner == message.channel:
                board.owner = None
                await write(f"Release board owner: {str(board.owner)}")
                await message.channel.send("ボードオーナーを離れました。")
            else:
                await message.channel.send("あなたはボードオーナーではありません。")
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
                    await message.channel.send("Scoreを変更しました")
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
