from typing import Dict, Any, List

import attr

from .message import Message
from .member import Member
from .options import Options


@attr.s(slots=True)
class Guild:
    """A simplistic dataclass representing a Guild"""

    id: int = attr.ib(eq=True)
    options: Options = attr.ib(eq=False, default=attr.Factory(Options))
    log_channel_id: int = attr.ib(eq=False, default=None)
    members: Dict[int, Member] = attr.ib(default=attr.Factory(dict), eq=False)

    # These messages should be the same as `member.messages`, I think
    messages: List[Message] = attr.ib(default=attr.Factory(list), eq=False)

    # So that plugins can access this data
    # key -> Plugin.__class__.__name__
    # Value -> Whatever they want to store
    addons: Dict[str, Any] = attr.ib(default=attr.Factory(dict), eq=False)
