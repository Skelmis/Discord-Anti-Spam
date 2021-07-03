AntiSpamHandler
===============

**Note, this is the main entrance to this entire package.
As such this should be the only thing you interact with.**

This handler propagation method also returns the following dictionary for you to use:

.. currentmodule:: antispam.anti_spam_handler

.. code-block:: python
    :linenos:

    {
        "should_be_punished_this_message": boolean,
        "was_warned": boolean,
        "was_kicked": boolean,
        "was_banned": boolean,
        "status": string,
        "warn_count": integer,
        "kick_count": integer,
        "duplicate_counter": integer,
        "pre_invoke_extensions": list,
        "after_invoke_extensions": list,
    }


.. autoclass:: AntiSpamHandler
    :members:
    :special-members: __init__
