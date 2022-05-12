Cache Choices
=============

Internally all data is 'cached' using an implementation
which implements :py:class:`antispam.abc.Cache`

In the standard package you have the following choices:
 - :py:class:`antispam.caches.MemoryCache` (Default)
 - :py:class:`antispam.caches.mongo.MongoCache`
 - :py:class:`antispam.caches.redis.RedisCache`

In order to use a cache other then the default one, 
simply pass in an instance of the cache you wish to
use with the ``cache`` kwarg when initialising your
``AntiSpamHandler``.

Alternately, use the ``AntiSpamHandler.set_cache`` method.

Once a cache is registered like so, there is nothing else you need to do. 
The package will simply use that caching mechanism.

Also note, AntiSpamHandler will call :py:meth:`antispam.abc.Cache.initialize`
before any cache operations are undertaken.

Redis Cache
***********

Here is an example, note ``RedisCache`` needs a extra argument.

.. code-block:: python
    :linenos:

    import discord
    from discord.ext import commands
    from redis import asyncio as aioredis

    from antispam import AntiSpamHandler
    from antispam.caches.redis import RedisCache

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    bot.handler = AntiSpamHandler(bot)

    redis = aioredis.from_url("redis://localhost")
    redis_cache: RedisCache = RedisCache(bot.handler, redis)
    bot.handler.set_cache(redis_cache)


MongoDB Cache
*************

Here is an example, note ``MongoCache`` needs a extra argument.

.. code-block:: python
    :linenos:

    import discord
    from discord.ext import commands

    from antispam import AntiSpamHandler
    from antispam.caches.mongo import MongoCache

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    bot.handler = AntiSpamHandler(bot)

    my_cache = MongoCache(bot.handler, "Mongo connection url")
    bot.handler.set_cache(my_cache)
