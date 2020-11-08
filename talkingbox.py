import random


class TalkingBox:
    next_only_word = []

    def __init__(self, errorch):
        self.error_notify_channel = errorch  # コンソール用のチャンネルを設定

    def append_line(self, filename, line):
        # ファイルに１行追加
        with open(filename, mode="a", encoding="utf-8") as f:
            f.write(f"\n{line}")

    async def seed_reply(self, channel, seed, word_list, fmt="%word%"):
        random.seed(seed)
        lis = []
        for w, per in word_list:
            lis.extend([w for _ in range(per)])
        word = random.choice(lis)
        msg = fmt.replace("%word%", word).replace("%seed%", seed)
        await channel.send(msg)
        random.seed()

    async def reply(self, channel, msg):
        # next_only_wordに該当する単語であれば、それを反応させて終了
        for word in self.next_only_word:
            if msg == word[0]:
                await channel.send(word[1])
                self.next_only_word.remove(word)
                return

        filelines = []
        # main.tbの読み込み - 1行ずつfilelinesリストとする
        with open("main.tb", "r", encoding="utf-8") as f:
            filelines = f.readlines()
        filelines.append("#")

        randomlines = []
        picknum = 1
        separator = "\n"
        chatflag = False
        # main.tbの中身を実際にインタプリットする
        while len(filelines) > 0:
            line = filelines.pop(0)
            if line.startswith("@call "):
                # @callから始まる場合、他のファイルを読み込んで、filelinesの先頭に挿入する
                try:
                    filename = line[6:].strip()
                    with open(filename, "r", encoding="utf-8") as f:
                        newfilelines = f.readlines()
                    filelines = newfilelines + filelines
                except:
                    await self.error_notify_channel.send(f"Error call TalkingBoxFile:{filename}")
                continue
            if line.startswith("//"):
                # //から始まる場合はコメント行として無視する
                continue
            if chatflag:
                # そのセクションの単語を拾い、最後まで拾ったらその中からrandomで送信
                if line[0] == "@":
                    continue
                elif line[0] == "#":
                    # 送信
                    #print(randomlines)
                    sendmsg = ""
                    for i in range(picknum):
                        if i != 0: sendmsg += separator
                        sendmsg += random.choice(randomlines).strip()
                    await channel.send(sendmsg)
                    randomlines = []
                    chatflag = False
                    picknum = 1
                    separator = "\n"
                elif line != "" and line != "\n":
                    # randomで追加する
                    randomlines.append(line)
            else:
                # セクションの頭から見ていき、引っかかるものがあるのかをチェック：あればchatflagを立てて送信を行うようにする
                if line.startswith("@include="):
                    line_words = line[9:].strip().split(',')
                    #print(f"Judge: {line_words}")
                    for w in line_words:
                        if msg.lower().count(w.lower()):
                            chatflag = True
                            break
                elif line.startswith("@equal="):
                    line_words = line[7:].strip().split(',')
                    for w in line_words:
                        if msg.lower() == w.lower():
                            chatflag = True
                            break
                elif line.startswith("@equal:"):
                    # 任意の個数まとめて送信する
                    line_msg = line[7:]
                    num = 0
                    mini = 0
                    faze_range = False
                    for i in range(len(line_msg)):
                        if line_msg[i].isdecimal():
                            num = num * 10 + int(line_msg[i])
                        elif line_msg[i] == "-":
                            if faze_range:
                                raise Exception("illegal range set")
                            faze_range = True
                            mini = num
                            num = 0
                        elif line_msg[i] == "=":
                            line_words = line_msg[(i+1):].strip().split(',')
                            for w in line_words:
                                if msg.lower() == w.lower():
                                    chatflag = True
                                    picknum = num
                                    if faze_range:
                                        if mini >= num:
                                            raise Exception("illegal range")
                                        picknum = random.randrange(mini, num+1)
                                    break
                            break
                        else:
                            print(f"Error: {line}")
                            break

                elif line.startswith("@separator="):
                    # 複数まとめて送信する際にその区切りとなる文字を変更する(デフォルトは改行)
                    line_msg = line[11:].replace("\n", "").replace("\r","").replace("<br>","\n")
                    if len(line_msg) > 0:
                        separator = line_msg
                    
                elif line[0] == "@":
                    # 1行bot
                    try:
                        resword, responce = line[1:].split('|')
                        reswords = resword.split(",")
                        for w in reswords:
                            if msg.lower().count(w.strip()): 
                                await channel.send(responce)
                                break
                    except Exception as e:
                        print(f"Error execute {line}")
                        print(f"Errorcontent: {str(e)}")
                        continue
                elif line[0] == "#":
                    separator = "\n"
