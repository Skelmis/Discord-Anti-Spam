.. DPY Anti-Spam documentation master file, created by
   sphinx-quickstart on Fri Sep 18 23:28:30 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DPY Anti-Spam's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Main Interface:

   modules/main/main.rst
   modules/main/options.rst
   modules/main/caches.rst
   modules/main/core.rst

.. toctree::
   :maxdepth: 2
   :caption: Plugin Framework

   modules/plugins/plugins.rst
   modules/plugins/schema.rst

.. toctree::
   :maxdepth: 2
   :caption: Object Reference:

   modules/objects/objects.rst
   modules/objects/abc.rst
   modules/objects/exceptions.rst
   modules/objects/guild.rst
   modules/objects/member.rst
   modules/objects/memory.rst
   modules/objects/message.rst
   modules/objects/redis.rst

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
