Example usages
==============

Super duper basic bot
---------------------

.. code-block:: python
    :linenos:

    import discord
    from discord.ext import commands

    from AntiSpam import AntiSpamHandler

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    bot.handler = AntiSpamHandler(bot)


    @bot.event
    async def on_ready():
        # On ready, print some details to standard out
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


    @bot.event
    async def on_message(message):
        bot.handler.propagate(message)
        await bot.process_commands(message)


    if __name__ == "__main__":
        bot.run("Bot Token Here")


How to use templating in a string
---------------------------------

.. code-block:: python
    :linenos:

    from discord.ext import commands

    from AntiSpam import AntiSpamHandler

    bot = commands.Bot(command_prefix="!")
    bot.handler = AntiSpamHandler(bot, ban_message="$MENTIONUSER you are hereby banned from $GUILDNAME for spam!")

    @bot.event
    async def on_ready():
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")

    @bot.event
    async def on_message(message):
        bot.handler.propagate(message)
        await bot.process_commands(message)

    if __name__ == "__main__":
        bot.run("Bot Token")


How to use templating in embeds
-------------------------------

.. code-block:: python
    :linenos:


    from discord.ext import commands

    from AntiSpam import AntiSpamHandler

    bot = commands.Bot(command_prefix="!")

    warn_embed_dict = {
        "title": "**Dear $USERNAME**",
        "description": "You are being warned for spam, please stop!",
        "timestamp": True,
        "color": 0xFF0000,
        "footer": {"text": "$BOTNAME", "icon_url": "$BOTAVATAR"},
        "author": {"name": "$GUILDNAME", "icon_url": "$GUILDICON"},
        "fields": [
            {"name": "Current warns:", "value": "$WARNCOUNT", "inline": False},
            {"name": "Current kicks:", "value": "$KICKCOUNT", "inline": False},
        ],
    }
    bot.handler = AntiSpamHandler(bot, guild_warn_message=warn_embed_dict)

    @bot.event
    async def on_ready():
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")

    @bot.event
    async def on_message(message):
        bot.handler.propagate(message)
        await bot.process_commands(message)

    if __name__ == "__main__":
        bot.run("Bot Token")


Custom Punishments
------------------

.. code-block:: python
    :linenos:

    from discord.ext import commands

    from AntiSpam import AntiSpamHandler

    bot = commands.Bot(command_prefix="!")
    bot.handler = AntiSpamHandler(bot, guild_warn_message=warn, no_punish=True)
    bot.tracker = AntiSpamTracker(bot.handler, 3)
    # 3 Being how many 'punishment requests' before is_spamming returns True

    @bot.event
    async def on_ready():
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        data = await bot.handler.propagate(message)
        bot.tracker.update_cache(message, data)

        if bot.tracker.is_spamming(message):
          # Do things like mute the user

        await bot.process_commands(message)

    if __name__ == "__main__":
        bot.run("Bot Token")