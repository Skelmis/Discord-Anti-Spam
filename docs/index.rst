.. DPY Anti-Spam documentation master file, created by
   sphinx-quickstart on Fri Sep 18 23:28:30 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DPY Anti-Spam's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Main Interface:

   modules/handler.rst
   modules/options.rst
   modules/examples.rst
   modules/logging.rst
   modules/optimisation.rst

.. toctree::
   :maxdepth: 2
   :caption: Extension Framework

   modules/ext/base.rst
   modules/ext/schema.rst
   modules/ext/custom_punishment.rst

.. toctree::
   :maxdepth: 2
   :caption: Object Reference:

   modules/guild.rst
   modules/user.rst
   modules/message.rst
   modules/util.rst
   modules/exceptions.rst

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
