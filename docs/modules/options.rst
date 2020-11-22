Message Options
===============

This package utilises safe conversions for message arguments within strings.

The following are all the options you as the user have:

* **$MENTIONUSER** - This will attempt to mention the user, uses ``discord.Member.mention``
* **$USERNAME** - This will attempt to state the user's name, uses ``discord.Member.display_name``
* **$USERID** - This will attempt to state the user's id, uses ``discord.Member.id``
* **$GUILDNAME** - This will attempt to state the guild's name, uses ``discord.Guild.name``
* **$GUILDID** - This will attempt to state the guild's id, uses ``discord.Guild.id``

You can include the above options in the following arguments
when you initialize the package:

* **guild_warn_message**
* **guild_kick_message**
* **guild_ban_message**
* **user_kick_message**
* **user_ban_message**

Example usage:

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