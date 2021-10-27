"""
The MIT License (MIT)

Copyright (c) 2020-Current Skelmis

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from typing import Set, Dict, Any, Union

import attr


@attr.s(slots=True, eq=True, kw_only=True)
class Options:
    """Options for the AntiSpamHandler, see :py:class:`antispam.AntiSpamHandler` for explanations"""

    # Ints
    warn_threshold: int = attr.ib(default=3, validator=attr.validators.instance_of(int))
    kick_threshold: int = attr.ib(default=2, validator=attr.validators.instance_of(int))
    ban_threshold: int = attr.ib(default=2, validator=attr.validators.instance_of(int))
    message_interval: int = attr.ib(
        default=30000, validator=attr.validators.instance_of(int)
    )
    message_duplicate_count: int = attr.ib(
        default=5, validator=attr.validators.instance_of(int)
    )
    message_duplicate_accuracy: int = attr.ib(
        default=90, validator=attr.validators.instance_of(int)
    )

    # delete_after
    guild_ban_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    guild_kick_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    member_ban_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    guild_warn_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )
    member_kick_message_delete_after: int = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(int)),
    )

    # Strings
    guild_warn_message: Union[str, dict] = attr.ib(
        default="$MEMBERNAME was warned for spamming/sending duplicate messages.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    guild_kick_message: Union[str, dict] = attr.ib(
        default="$MEMBERNAME was kicked for spamming/sending duplicate messages.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    guild_ban_message: Union[str, dict] = attr.ib(
        default="$MEMBERNAME was banned for spamming/sending duplicate messages.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    member_warn_message: Union[str, dict] = attr.ib(
        default="Hey $MENTIONMEMBER, please stop spamming/sending duplicate messages.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    member_kick_message: Union[str, dict] = attr.ib(
        default="Hey $MENTIONMEMBER, you are being kicked from $GUILDNAME for spamming/"
        "sending duplicate messages.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    member_ban_message: Union[str, dict] = attr.ib(
        default="Hey $MENTIONMEMBER, you are being banned from $GUILDNAME for spamming/"
        "sending duplicate messages.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    member_failed_kick_message: Union[str, dict] = attr.ib(
        default="I failed to punish you because I lack permissions, but still you shouldn't spam.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )
    member_failed_ban_message: Union[str, dict] = attr.ib(
        default="I failed to punish you because I lack permissions, but still you shouldn't spam.",
        kw_only=True,
        validator=attr.validators.instance_of((str, dict)),
    )

    # Sets
    ignored_members: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )
    ignored_channels: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )
    ignored_roles: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )
    ignored_guilds: Set[int] = attr.ib(
        default=attr.Factory(set),
        validator=attr.validators.instance_of(set),
        converter=set,
    )

    # Booleans
    delete_spam: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )
    ignore_bots: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )
    warn_only: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )
    no_punish: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )
    mention_on_embed: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )
    delete_zero_width_chars: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )

    # Core punishment settings
    per_channel_spam: bool = attr.ib(
        default=False, validator=attr.validators.instance_of(bool)
    )  # False implies per_user_per_guild

    # TODO Implement this
    # Catches 5 people saying the same thing
    is_per_channel_per_guild: bool = attr.ib(
        default=True, validator=attr.validators.instance_of(bool)
    )

    # Add on option storage for plugins
    addons: Dict[str, Any] = attr.ib(
        default=attr.Factory(dict), validator=attr.validators.instance_of(dict)
    )
