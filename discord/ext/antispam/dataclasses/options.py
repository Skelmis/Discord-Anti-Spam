from typing import List

import attr


@attr.s(slots=True, eq=True, kw_only=True)
class Options:
    """Options for the AntiSpamHandler"""

    # Ints
    warn_threshold: int = attr.ib(default=3)
    kick_threshold: int = attr.ib(default=2)
    ban_threshold: int = attr.ib(default=2)
    message_interval: int = attr.ib(default=30000)
    message_duplicate_count: int = attr.ib(default=5)
    message_duplicate_accuracy: int = attr.ib(default=90)

    # Strings
    guild_warn_message: str = attr.ib(
        default="Hey $MENTIONUSER, please stop spamming/sending duplicate messages.",
        kw_only=True,
    )
    guild_kick_message: str = attr.ib(
        default="$USERNAME was kicked for spamming/sending duplicate messages.",
        kw_only=True,
    )
    guild_ban_message: str = attr.ib(
        default="$USERNAME was banned for spamming/sending duplicate messages.",
        kw_only=True,
    )
    user_kick_message: str = attr.ib(
        default="Hey $MENTIONUSER, you are being kicked from $GUILDNAME for spamming/"
        "sending duplicate messages.",
        kw_only=True,
    )
    user_ban_message: str = attr.ib(
        default="Hey $MENTIONUSER, you are being banned from $GUILDNAME for spamming/"
        "sending duplicate messages.",
        kw_only=True,
    )
    user_failed_kick_message: str = attr.ib(
        default="I failed to punish you because I lack permissions, but still you shouldn't spam.",
        kw_only=True,
    )
    user_failed_ban_message: str = attr.ib(
        default="I failed to punish you because I lack permissions, but still you shouldn't spam.",
        kw_only=True,
    )
    # TODO Implement a log channel

    # Lists
    ignore_users: List[int] = attr.ib(default=attr.Factory(list))
    ignore_channels: List[int] = attr.ib(default=attr.Factory(list))
    ignore_roles: List[int] = attr.ib(default=attr.Factory(list))
    ignore_guilds: List[int] = attr.ib(default=attr.Factory(list))

    # Booleans
    delete_spam: bool = attr.ib(default=True)
    ignore_bots: bool = attr.ib(default=True)
    warn_only: bool = attr.ib(default=False)
    no_punish: bool = attr.ib(default=False)
    per_channel_spam: bool = attr.ib(default=False)
    delete_zero_width_chars: bool = attr.ib(default=True)
