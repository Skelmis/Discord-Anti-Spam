Welcome to DPY Anti-Spam's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Primary Interface:

   modules/main/main.rst
   modules/main/caches.rst
   modules/main/examples.rst
   modules/main/logging.rst
   modules/main/template.rst

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
   modules/plugins/tracker.rst
   modules/plugins/mentions.rst
   modules/plugins/stats.rst

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
   modules/objects/data.rst

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
