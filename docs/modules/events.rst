Custom Events
=============

This package utilises custom discord.py events for punishments.
This system will be further rolled out down the line to the standard lib.


Anti Mass Mentions
==================

.. code-block:: python
    :linenos:

    from antispam.ext import MassMentionPunishment

    @bot.event
    async def on_mass_mention_punishment(payload: MassMentionPunishment):
        # Your code here

The ``payload`` is an instance of the following:

.. autoclass:: antispam.ext.anti_mass_mention.MassMentionPunishment
    :members:
