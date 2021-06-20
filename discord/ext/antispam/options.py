from typing import List

import attr


@attr.s(slots=True)
class Options:
    """Options for the AntiSpamHandler"""

    # Ints
    warn_threshold: int = attr.ib(default=3, kw_only=True)
    kick_threshold: int = attr.ib(default=2, kw_only=True)
    ban_threshold: int = attr.ib(default=2, kw_only=True)
    message_interval: int = attr.ib(default=30000, kw_only=True)
    message_duplicate_count: int = attr.ib(default=5, kw_only=True)
    message_duplicate_accuracy: int = attr.ib(default=90, kw_only=True)

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
    ignore_users: List[int] = attr.ib(default=attr.Factory(list), kw_only=True)
    ignore_channels: List[int] = attr.ib(default=attr.Factory(list), kw_only=True)
    ignore_roles: List[int] = attr.ib(default=attr.Factory(list), kw_only=True)
    ignore_guilds: List[int] = attr.ib(default=attr.Factory(list), kw_only=True)

    # Booleans
    delete_spam: bool = attr.ib(default=True, kw_only=True)
    ignore_bots: bool = attr.ib(default=True, kw_only=True)
    warn_only: bool = attr.ib(default=False, kw_only=True)
    no_punish: bool = attr.ib(default=False, kw_only=True)
    per_channel_spam: bool = attr.ib(default=False, kw_only=True)
    delete_zero_width_chars: bool = attr.ib(default=True, kw_only=True)
