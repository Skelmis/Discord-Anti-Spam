from enum import Enum


class IgnoreType(Enum):
    """
    This enum should be using within the following methods:

    - :py:meth:`antispam.AntiSpamHandler.add_ignored_item`
    - :py:meth:`antispam.AntiSpamHandler.remove_ignored_item`

    It is used to signify the type of item you wish to
    ignore within any following propagate calls.
    """

    MEMBER = 0
    CHANNEL = 1
    GUILD = 2
    ROLE = 3
