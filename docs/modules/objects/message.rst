Message Reference
=================


*You should not be creating this object yourself.
It is just useful to understand how they work for say,
plugin development.*

Internally the Message object just takes a few attributes
from ``discord.Message`` and stores them in a smaller object
to save on memory. It also maintains a ``is_duplicate`` bool
for internal reasons.

.. currentmodule:: antispam.dataclasses.message

.. autoclass:: Message
    :members:
    :undoc-members:
    :special-members: __init__
