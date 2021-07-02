from typing import Dict, List, Any, Union

import attr
import discord


from .member import Member
from .options import Options


@attr.s(slots=True)
class Guild:
    """A simplistic dataclass representing a Guild"""

    id: int = attr.ib(eq=True)
    options: Options = attr.ib(eq=False)
    log_channel: discord.TextChannel = attr.ib(eq=False)
    members: Dict[int, Member] = attr.ib(default=attr.Factory(dict), eq=False)

    # So that plugins can access this data
    # key -> Plugin.__class__.__name__
    # Value -> Whatever they want to store
    addons: Dict[str, Any] = attr.ib(default=attr.Factory(dict), eq=False)
