class Board:
    channel = None
    random_ch = None
    owner = None
    locked = False
    joiner = []
    answers_judge = []
    prev = []

    def __init__(self, main_channel, random_channel):
        self.channel = main_channel
        self.random_ch = random_channel

    def is_owner(self, channel):
        return channel == self.owner and self.owner != None

    def is_joiner(self, channel):
        for j in self.joiner:
            if channel == j.channel:
                return True
        return False

    async def joiner_notify(self, msg = ""):
        if self.owner == None:
            await write("Board Owner is none")
        else:
            msg += f"\n☆現在の参加者: {len(self.joiner)}人"
            for player in self.joiner:
                msg += f"\n{str(player.name)[20:]}"
            await self.owner.send(msg)

    async def join(self, channel):
        for pl in self.joiner:
            if pl.is_equal(channel):
                await channel.send(f"既に参加しています。退出の場合は `board exit` と送ってください。")
                return 

        wb = WhiteBoard(channel, self)
        self.joiner.append(wb)
        await channel.send(f"参加しました。退出の場合は `board exit` と送ってください。")
        await self.joiner_notify(f"{wb.name}さんが参加")

    async def exit(self, channel):
        for idx in range(len(self.joiner)):
            if self.joiner[idx].is_equal(channel):
                exit_name = self.joiner[idx].name
                del self.joiner[idx]
                await channel.send(f"退出しました。")
                await self.joiner_notify(f"{exit_name}さんが退出")
                return 

        await channel.send(f"ボードに参加していません。 `board join` でJoinが可能です。")

    async def send_info(self):
        await self.channel.send("基本的にこのbotへのDMですべてのことを行います。\n参加されるときはbot宛に `board join` と送ってください。\n解答は参加後に単にbot宛に解答を送ればOKです。\n退出の際は `board exit` とbot宛に送ってください。")

    async def correct_check_by_id(self, idx):
        try:
            idxs = list(map(int,idx.strip().split()))
        except:
            await self.owner.send("cに続けて、`c1 4 5 6` のように空白区切りで正誤状況を反転させるプレーヤーを選択してください")
            return
        judge = ""
        answers = []
        for i in idxs:
            try:
                answers.append((self.joiner[i].content, (not self.joiner[i].correct)))
            except Exception as e:
                await self.owner.send(f"{i}は見つかりません")
                print(str(e))
        self.set_correct(answers)
        await self.send_correct_status(self.owner)
        self.answers_judge.extend(answers)

    def set_correct(self, answer_list):
        for j in self.joiner:
            for answer in answer_list:
                if j.content == answer[0]: 
                    j.correct = answer[1]
    
    async def reset_correct(self):
        self.answers_judge = []
        for j in self.joiner:
            j.correct = False
        
    async def open(self, answer):
        for _ in range(len(self.prev)):
            m = self.prev.pop()
            await m.delete()
        ans = await self.channel.send("**" + answer + "**")
        await self.random_ch.send("> " + answer)
        cor = await self.send_correct_status(self.channel, False)
        self.prev.append(ans)
        self.prev.append(cor)
        print(self.prev)
        ra = await self.next()
        self.prev.append(ra)

    async def send_correct_status(self, channel, idxshow = True):
        cor = []
        wro = []
        for idx in range(len(self.joiner)):
            if self.joiner[idx].correct:
                cor.append(f"{str(idx) + '.' if idxshow else '' }{self.joiner[idx].name}: {self.joiner[idx].content}")
            else:
                wro.append(f"{idx}.{self.joiner[idx].name}: {self.joiner[idx].content}")
        msg = "○正解者\n" + "\n".join(cor) + "\n\n●不正解者\n" + "\n".join(wro)
        return await channel.send(msg)

    async def lock(self):
        self.locked = True
        for j in self.joiner:
            await j.send("ボードをロックしました。以降、変更はできません。")
        await self.owner.send("ボードロック")
        await self.send_correct_status(self.owner)

    async def next(self, plus_score = 1):
        self.locked = False
        for j in self.joiner:
            if j.correct: j.score += plus_score
            await j.reset()
        ra = await self.send_rank(self.channel)
        await self.owner.send("Next")
        return ra

    
    async def send_rank(self, channel):
        self.joiner.sort(key=lambda x: x.score, reverse=True)
        ranking = "★スコア"
        r = 1
        for j in self.joiner:
            ranking += f"\n{r}. {j.name} - {j.score}点"
            r += 1
        return await channel.send(ranking)

    async def joiner_write(self, channel, content):
        for j in self.joiner:
            if j.is_equal(channel):
                if self.locked:
                    await channel.send("回答はロックされています")
                    return
                await j.write(content)
                await self.send_correct_status(self.owner)
                print(f"W {channel} {content}")
                return
        raise Exception(f"Joinner is not found: {channel}")

class WhiteBoard:
    content = ""
    score = 0
    correct = False
    def __init__(self, _channel, parent):
        self.channel = _channel
        self.name = str(self.channel)[20:]
        self.parent_board = parent
    
    def is_equal(self, jch):
        return self.name == str(jch)[20:]
        

    async def write(self, new_content):
        self.content = new_content.strip().replace("\n", " ").replace("\r","")
        await self.channel.send(f"{self.content}と記入しました。")
        self.correct = False
        for ans in self.parent_board.answers_judge:
            if ans[0] == self.content:
                self.correct = ans[1]


    async def reset(self):
        self.content = ""
        self.correct = False
        await self.channel.send(f"ボードが白紙に戻されました、現在のあなたのスコアは{self.score}点です。")

    async def send(self, msg):
        await self.channel.send(msg)

