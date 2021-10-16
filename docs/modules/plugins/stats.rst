Statistics Plugin
=================

A simplistic approach to statistics gathering
which works by default and requires no further setup.

.. code-block:: python
    :linenos:

    from discord.ext import commands

    from antispam import AntiSpamHandler
    from antispam.ext import Stats

    bot = commands.Bot(command_prefix="!")
    bot.handler = AntiSpamHandler(bot, no_punish=True)
    bot.stats = Stats(bot.handler)
    bot.handler.register_extension(bot.stats)

    # We don't want to collect stats on guild 12345
    # So lets ignore it on this plugin
    bot.stats.blacklisted_guilds.add(12345)


    @bot.event
    async def on_ready():
        # On ready, print some details to standard out
        print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


    if __name__ == "__main__":
        bot.run("Bot Token")

.. currentmodule:: antispam.plugins

.. autoclass:: Stats
    :members:
    :undoc-members:
    :special-members: __init__