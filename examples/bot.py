import discord
from discord.ext import commands

from AntiSpam import AntiSpamHandler
from jsonLoader import read_json

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

file = read_json("token")

# Generally you only need/want AntiSpamHandler(bot)
bot.handler = AntiSpamHandler(bot, 1, ignore_bots=False)


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


@bot.event
async def on_message(message):
    bot.handler.propagate(message)
    await bot.process_commands(message)
    
    
@bot.event
async def on_member_join(member):
    bot.handler.update_user_state(member)
    

if __name__ == "__main__":
    bot.run(file["token"])
