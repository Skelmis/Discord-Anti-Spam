Example usages
==============

Note, all of these examples are for discord.py.
If you would like another library here, let me know.

Super duper basic bot
---------------------

.. code-block:: python
    :linenos:

    import discord
    from discord.ext import commands

    from antispam import AntiSpamHandler

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    bot.handler = AntiSpamHandler(bot)


    @bot.event
    async def on_ready():
        # On ready, print some details to standard out
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


    @bot.event
    async def on_message(message):
        await bot.handler.propagate(message)
        await bot.process_commands(message)


    if __name__ == "__main__":
        bot.run("Bot Token Here")


Basic Hikari bot
----------------

.. code-block:: python
    :linenos:

    import hikari
    from antispam import AntiSpamHandler

    bot = hikari.GatewayBot(
        token="..."
    )
    handler = AntiSpamHandler(bot, is_using_hikari=True)

    @bot.listen()
    async def ping(event: hikari.GuildMessageCreateEvent) -> None:
        if event.is_bot or not event.content:
            return

        await handler.propagate(event.message)

    bot.run()


How to use templating in a string
---------------------------------

.. code-block:: python
    :linenos:

    from discord.ext import commands

    from antispam import AntiSpamHandler, Options

    bot = commands.Bot(command_prefix="!")
    bot.handler = AntiSpamHandler(bot, options=Options(ban_message="$MENTIONUSER you are hereby banned from $GUILDNAME for spam!"))

    @bot.event
    async def on_ready():
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")

    @bot.event
    async def on_message(message):
        await bot.handler.propagate(message)
        await bot.process_commands(message)

    if __name__ == "__main__":
        bot.run("Bot Token")

Cog Based Usage
---------------

.. code-block:: python
    :linenos:

    from discord.ext import commands
    from antispam import AntiSpamHandler

    class AntiSpamCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.bot.handler = AntiSpamHandler(self.bot)

        @commands.Cog.listener()
        async def on_ready(self):
            print("AntiSpamCog is ready!\n-----\n")

        @commands.Cog.listener()
        async def on_message(self, message):
            await self.bot.handler.propagate(message)

    def setup(bot):
        bot.add_cog(AntiSpamCog(bot))


How to use templating in embeds
-------------------------------

.. code-block:: python
    :linenos:


    from discord.ext import commands

    from antispam import AntiSpamHandler, Options

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
    bot.handler = AntiSpamHandler(bot, options=Options(guild_warn_message=warn_embed_dict))

    @bot.event
    async def on_ready():
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")

    @bot.event
    async def on_message(message):
        await bot.handler.propagate(message)
        await bot.process_commands(message)

    if __name__ == "__main__":
        bot.run("Bot Token")


Custom Punishments
------------------

.. code-block:: python
    :linenos:

    from discord.ext import commands

    from antispam import AntiSpamHandler
    from antispam.plugins import AntiSpamTracker, Options

    bot = commands.Bot(command_prefix="!")
    bot.handler = AntiSpamHandler(bot, options=Options(no_punish=True))
    bot.tracker = AntiSpamTracker(bot.handler, 3) # 3 Being how many 'punishment requests' before is_spamming returns True
    bot.handler.register_extension(bot.tracker)


    @bot.event
    async def on_ready():
        # On ready, print some details to standard out
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


    @bot.event
    async def on_message(message):
        await bot.handler.propagate(message)

        if bot.tracker.is_spamming(message):
            # Insert code to mute the user

            # Insert code to tell admins

            # ETC
            bot.tracker.remove_punishments(message)

        await bot.process_commands(message)

    if __name__ == "__main__":
        bot.run("Bot Token")
