AntiSpamHandler
===============

**Note, this is the main entrance to this entire package.
As such this should be the only thing you interact with.**

This handler propagation method also returns the following dictionary for you to use:

.. code-block::
    :linenos:

    {
        "warn_count": self.warn_count,
        "kick_count": self.warn_count,
        "duplicate_counter": self.get_correct_duplicate_count(),
        "was_punished_this_message": was_punished,
    }

.. automodule:: AntiSpam.AntiSpamHandler
    :members:
    :special-members: __init__
