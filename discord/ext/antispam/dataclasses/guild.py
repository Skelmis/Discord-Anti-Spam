from typing import Dict, List

import attr

from . import Message, Member
from discord.ext.antispam.dataclasses.options import Options


@attr.s(slots=True)
class Guild:
    """A simplistic dataclass representing a Guild"""

    id: int = attr.ib(eq=True)
    options: Options = attr.ib(eq=False)
    members: Dict[int:Member] = attr.ib(default=attr.Factory(dict), eq=False)

    # For storing spam at a guild level
    messages: List[Message] = attr.ib(default=attr.Factory(list), eq=False)
