Extension Class Schema
======================

All extensions that aim to be used as a registered
extension *within* ``AntiSpamHandler`` should
have at least the following class layout.


Pre-invoke Schema
-----------------

.. code-block:: python
    :linenos:

    class Placeholder:
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

    class Placeholder:
        def __init__(self):
            self.is_pre_invoke = False

        async def propagate(self, message: discord.Message, propagate_data: dict) -> dict:
            # Do your code stuff here


The only difference between these two schema's, outside of ``self.is_pre_invoke``
being different, is that the after-invoke method will also be given an
extra argument which is a deepcopy of the data returned by ``propagate``