import datetime

import attr

from antispam.util import get_aware_time


@attr.s(slots=True)
class Message:
    """A simplistic dataclass representing a Message"""

    id: int = attr.ib()
    channel_id: int = attr.ib()
    guild_id: int = attr.ib()
    author_id: int = attr.ib()
    content: str = attr.ib()
    creation_time: datetime.datetime = attr.ib(default=attr.Factory(get_aware_time))
    is_duplicate: bool = attr.ib(default=False)
