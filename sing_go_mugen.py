# coding=utf-8
import discord, random

client = discord.Client()

## 以下クライアントの処理関数
@client.event
async def on_ready():
    print("Login")

@client.event
async def on_message(message):
    if message.author.bot: return
    msg = message.content

    print(msg)

token = "sdfgbiousadhgipousahgbaophgu"
client.run(token)
