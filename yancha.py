from discord.ext import tasks, commands
import json
import datetime


class YanchaBot(commands.Bot):
    @tasks.loop(minutes=1)
    async def every_minutes_check(self):
        dt_now = datetime.datetime.now()
        await main.send(f"Hello. Now: {dt_now.hour}:{dt_now.minute}")


bot = YanchaBot(command_prefix="$")


@bot.event
async def on_ready():
    global main
    print("On ready")
    main = bot.get_channel(conf["mocho-general"])
    bot.every_minutes_check.start()


@bot.command(name="append")
async def _append(ctx, cmd, *arg):
    await main.send(cmd)
    await main.send(arg)


conf = {}
if __name__ == "__main__":
    print("Program Start")
    with open("config.json", "r") as f:
        conf = json.load(f)

    bot.run(conf["token"])
