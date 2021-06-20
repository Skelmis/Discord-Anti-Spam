from typing import Dict

import attr

from .member import Member
from discord.ext.antispam.options import Options


@attr.s(slots=True)
class Guild:
    """A simplistic dataclass representing a Guild"""

    id: int = attr.ib(eq=True)
    options: Options = attr.ib(eq=False)
    has_custom_options: bool = attr.ib(
        default=False
    )  # TODO Remove this in favour of Options==Options checks
    members: Dict[int:Member] = attr.ib(default=attr.Factory(dict), eq=False)
