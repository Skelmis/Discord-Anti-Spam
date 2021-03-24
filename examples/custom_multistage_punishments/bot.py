import discord
from discord.ext import commands

from AntiSpam import AntiSpamHandler
from testing.jsonLoader import read_json

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

file = read_json("token")

# Generally you only need/want AntiSpamHandler(bot)
bot.handler = AntiSpamHandler(bot, ignore_bots=False)


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


@bot.event
async def on_message(message):
    await bot.handler.propagate(message)
    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(file["token"])
