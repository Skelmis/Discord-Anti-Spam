import discord
from discord.ext import commands

from AntiSpam import AntiSpamHandler
from jsonLoader import read_json

bot = commands.Bot(command_prefix="!")

file = read_json("token")

bot.handler = AntiSpamHandler(bot, 709360360456454155)


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


if __name__ == "__main__":
    bot.run(file["token"])
