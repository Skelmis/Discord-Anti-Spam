from typing import List, Dict

import attr

from .message import Message


@attr.s(slots=True)
class Member:
    """A simplistic dataclass representing a Member"""

    id: int = attr.ib(eq=True)
    warn_count: int = attr.ib(default=0, eq=False)
    kick_count: int = attr.ib(default=0, eq=False)
    duplicate_count: int = attr.ib(default=0, eq=False)
    duplicate_channel_counter_dict: Dict[int:int] = attr.ib(
        default=attr.Factory(dict), eq=False
    )
    _in_guild: bool = attr.ib(default=True, eq=False)
    messages: List[Message] = attr.ib(default=attr.Factory(list), eq=False)
