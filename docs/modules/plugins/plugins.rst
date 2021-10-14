Package Plugin System
=====================

This package features feature a built in plugins framework soon.
This framework can be used to hook into the ``propagate`` method and run
as either a **pre_invoke** or **after_invoke** (Where **invoke** is
the built in **propagate**)

All registered extensions **must** subclass ``BasePlugin``

A plugin can do anything, from AntiProfanity to AntiInvite.
Assuming it is class based and follows the required schema you
can easily develop your own plugin that can be run whenever the
end developer calls ``await AntiSpamHandler.propagate()``

Some plugins don't need to be registered as an extension.
A good example of this is the ``AntiSpamTracker`` class.
This class does not need to be invoked with ``propagate`` as
it can be handled by the end developer for finer control.
However, it can also be used as a plugin if users are
happy with the default behaviour.

Any plugin distributed under the antispam package needs to be lib agnostic,
so as to not a dependency of something not in use.

Plugin Blacklisting
-------------------

Plugins provide a simplistic interface for skipping execution in any given guild.
Simply add the guilds id to the set located under the `Plugin.blacklisted_guilds`
variable and then this plugin will not be called for said guild.

Custom Punishments
------------------

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


Call Stack
----------

* Initially all checks are run, these are the checks baked into ``AntiSpamHandler``
    * You cannot avoid these checks, if you wish to mitigate them you should
      set them to values that will not be triggered
    * An option to run code before checks may be added in a future version,
      if this is something you would like, jump into discord and let me know!
      If I know people want features, they get done quicker
* Following that, all pre-invoke plugins will be run
    * If the guild this was called on is within `Plugin.blacklisted_guilds`
      then execution will be skipped and we move onto the next plugin.
    * The ordered that these are run is loosely based on the order that
      plugins were registered. Do not expect any form of runtime
      ordering however. You should build them around the idea that they
      are guaranteed to run before ``AntiSpamHandler.propagate``, not
      other plugins.
    * Returning ``cancel_next_invocation: True`` will result in ``propagate`` returning
      straight away. It will then return the dictionary of currently processed `pre_invoke_extensions`
* Run ``AntiSpamHandler.propagate``
    * If any pre-invoke plugin has returned a True value for ``cancel_next_invocation``
      then this method, and any after_invoke extensions will not be called.
* Run all after-invoke plugins
    * If the guild this was called on is within `Plugin.blacklisted_guilds`
      then execution will be skipped and we move onto the next plugin.
    * After_invoke plugins get output from both ``AntiSpamHandler``
      and all pre-invoke plugins as a method argument