Cache Choices
=============

Internally all data is 'cached' using an implementation
which implements ``Cache``. 

In the standard package you have the following choices:
 - Memory (Default)
 - Redis (Not yet implemented)

In order to use a cache other then the default one, 
simply pass in an instance of the cache you wish to
use with the ``cache`` kwarg when initalising your
``AntiSpamHandler``.

Heres an example, note ``RedisCache`` will likely need arguments to init.

.. code-block:: python
    :linenos:

    import discord
    from discord.ext import commands

    from antispam import AntiSpamHandler, RedisCache

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    bot.handler = AntiSpamHandler(bot, cache=RedisCache())


Once a cache is registered like so, there is nothing else you need to do. 
The package will simply use that caching mechanism.