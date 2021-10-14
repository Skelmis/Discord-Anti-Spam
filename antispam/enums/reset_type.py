from enum import Enum


class ResetType(Enum):
    """
    This enum should be using with the following methods:

    - :py:meth:`antispam.AntiSpamHandler.reset_member_count`

    It is used to signify the type of reset
    you wish to apply to the given member.
    """

    WARN_COUNTER = 0
    KICK_COUNTER = 1
