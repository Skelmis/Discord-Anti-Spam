import discord
from redis import asyncio as aioredis
from discord.ext import commands

from antispam.caches import RedisCache
from antispam.dataclasses import Guild, Member, Message
from antispam.enums import Library
from jsonLoader import read_json

from antispam import AntiSpamHandler

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

file = read_json("token")

bot.handler = AntiSpamHandler(bot, library=Library.NEXTCORD)

redis = aioredis.from_url("redis://localhost")
redis_cache: RedisCache = RedisCache(bot.handler, redis)

bot.handler.set_cache(redis_cache)


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


@bot.event
async def on_message(message):
    # await bot.handler.propagate(message)
    await bot.process_commands(message)


@bot.command()
async def set(ctx):
    await redis_cache.set_guild(
        Guild(
            ctx.guild.id,
            members={
                ctx.author.id: Member(
                    ctx.author.id,
                    guild_id=ctx.guild.id,
                    messages=[
                        Message(
                            ctx.message.id,
                            ctx.channel.id,
                            ctx.guild.id,
                            ctx.author.id,
                            ctx.message.content,
                        )
                    ],
                ),
            },
        )
    )
    await ctx.send("set")


@bot.command()
async def get(ctx):
    async for iter in redis_cache.get_all_members(ctx.guild.id):
        print(iter)


if __name__ == "__main__":
    bot.run(file["token"])
