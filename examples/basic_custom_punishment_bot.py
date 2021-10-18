import discord
from discord.ext import commands

from antispam import AntiSpamHandler, Options
from antispam.plugins import AntiSpamTracker, MaxMessageLimiter
from jsonLoader import read_json

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

file = read_json("token")

bot.handler = AntiSpamHandler(bot, options=Options(no_punish=True))
bot.tracker = AntiSpamTracker(bot.handler, 3)
bot.handler.register_plugin(bot.tracker)


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


@bot.event
async def on_message(message):
    await bot.handler.propagate(message)

    if await bot.tracker.is_spamming(message):
        # Insert code to mute the user

        # Insert code to tell admins

        # ETC
        await bot.tracker.remove_punishments(message)

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(file["token"])
