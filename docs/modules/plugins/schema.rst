Plugin Class Schema
===================

All plugins that aim to be used as a registered
extension *within* ``AntiSpamHandler`` should
have at least the following class layout.

All registered plugins **must** subclass ``BasePlugin``


Pre-invoke Schema
-----------------

.. code-block:: python
    :linenos:

    from antispam import BasePlugin

    class Placeholder(BasePlugin):
        def __init__(self):
            self.is_pre_invoke = True

        async def propagate(self, message: discord.Message) -> dict:
            # Do your code stuff here

``self.is_pre_invoke`` is optional assuming your extension is using
a pre-invoke due to the nature of the implementation.

After-invoke Schema
-------------------

.. code-block:: python
    :linenos:

    from antispam import BasePlugin

    class Placeholder(BasePlugin):
        def __init__(self):
            self.is_pre_invoke = False

        async def propagate(self, message: discord.Message, propagate_data: CorePayload) -> dict:
            # Do your code stuff here


The only difference between these two schema's, outside of ``self.is_pre_invoke``
being different, is that the after-invoke method will also be given an
extra argument which is the data returned by ``propagate``


Cancelling Invocation
---------------------
If a key called ``cancel_next_invocation`` is ``True`` within
the return data from any extension, ``AntiSpamHandler.propagate``
will immediately return without executing any remaining extensions
or even ``AntiSpamHandler.propagate``

Example usage:
Say you want to use AntiSpamHandler, but only if the message doesnt
contain a secret word. You would create a pre-invoke extension, and
if the secret word is said you would set ``cancel_next_invocation``
to ``True`` and then ``AntiSpamHandler`` would ignore that message.
Thats quite cool aint it! Woop woop