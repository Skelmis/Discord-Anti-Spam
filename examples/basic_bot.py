import discord
from discord.ext import commands

from antispam.enums import Library
from jsonLoader import read_json

from antispam import AntiSpamHandler

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

file = read_json("token")

bot.handler = AntiSpamHandler(bot, library=Library.YOUR_LIBRARY_HERE)


@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


@bot.event
async def on_message(message):
    await bot.handler.propagate(message)
    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(file["token"])
