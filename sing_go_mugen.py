# coding=utf-8
import configparser, discord, random

client = discord.Client()

conf_ini = configparser.ConfigParser()
conf_ini.read('config.ini', encoding='utf-8')
if conf_ini == None:
    print("Not found 'config.ini'")
    exit()

ids = conf_ini["Sing" + conf_ini["Sing"]["Server"]]

## 以下クライアントの処理関数
@client.event
async def on_ready():
    print("Login")

@client.event
async def on_message(message):
    msg = message.content

    afk_id = int(ids["AFK"])
    guild_id = int(ids["GUILD"])
    talkch_id = int(ids["TALKCH"])

    if message.author.bot: return
    print(msg)
    mugen = client.get_channel(afk_id)

    if msg == "ねむれしんぐ":
        guild = client.get_guild(guild_id)
        sing = guild.get_member(int(conf_ini["Sing"]["Sing"]))
        await sing.move_to(mugen)
    elif msg == "roulette":
        zatsudan = client.get_channel(talkch_id)

        r = random.randrange(len(zatsudan.members))
        await zatsudan.members[r].move_to(mugen)

token = conf_ini["Mocho"]["Token"]
client.run(token)
