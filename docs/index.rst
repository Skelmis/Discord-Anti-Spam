Welcome to DPY Anti-Spam's documentation!
=========================================

DPY Anti-Spam supports discord.py and all forks out of
the box assuming they use the ``discord`` namespace.

If you want to use this with hikari, please enable it
by passing ``library=Library.HIKARI`` to the
``AntiSpamHandler`` constructor.


The package features some built in punishments, these are:

- Per member spam is treated as warns, then kicks followed by bans.
- Per channel spam starts off as a kick straight away followed by bans

.. toctree::
   :maxdepth: 2
   :caption: Primary Interface:

   modules/main/main.rst
   modules/main/caches.rst
   modules/main/modes.rst
   modules/main/examples.rst
   modules/main/logging.rst
   modules/main/template.rst
   modules/migrating.rst
   modules/changelog.rst

.. toctree::
   :maxdepth: 2
   :caption: Main Interaction Classes

   modules/interactions/enums.rst
   modules/interactions/options.rst
   modules/interactions/core.rst

.. toctree::
   :maxdepth: 2
   :caption: Plugin Framework

   modules/plugins/plugins.rst
   modules/plugins/schema.rst
   modules/plugins/storage.rst
   modules/plugins/tracker.rst
   modules/plugins/mentions.rst
   modules/plugins/stats.rst
   modules/plugins/logs.rst
   modules/plugins/limiter.rst

.. toctree::
   :maxdepth: 2
   :caption: Object Reference:

   modules/objects/objects.rst
   modules/objects/abc.rst
   modules/objects/exceptions.rst
   modules/objects/guild.rst
   modules/objects/member.rst
   modules/objects/message.rst
   modules/objects/redis.rst
   modules/objects/memory.rst
   modules/objects/mongo.rst
   modules/objects/data.rst
   modules/objects/base.rst
   modules/objects/substitute_args.rst
   modules/objects/base_plugin.rst

Install Notes
-------------
Initial install will get you a working version of this lib, however it is
recommended you also install **python-Levenshtein** to speed this up.
This does require c++ build tools, hence why it is not included
by default.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
