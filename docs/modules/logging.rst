Package Logging
===============

This package features a fairly decent set of built-in logging,
the recommend logging level is logging.WARNING or logging.INFO

Basic Usage
-------------

Add this into your main.py/bot.py file, be aware this will also setup
logging for discord.py and any other modules which use it.

.. code-block:: python
    :linenos:

    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(module)s | %(message)s",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=logging.INFO,
    )

A more full example,

.. code-block:: python
    :linenos:

    import logging

    import discord
    from discord.ext import commands

    from AntiSpam import AntiSpamHandler
    from jsonLoader import read_json

    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(module)s | %(message)s",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=logging.INFO,
    )

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
