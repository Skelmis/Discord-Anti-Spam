from typing import Protocol

from .guild import Guild
from .member import Member
from .message import Message


class Cache(Protocol):
    """A generic Protocol for any Cache to implement"""

    async def get_guild(self, guild_id: int) -> Guild:
        """Fetch a Guild dataclass populated with members"""

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        """Fetch a Member dataclass populated with messages"""

    async def add_message(self, message: Message) -> None:
        """
        Adds a Message to the relevant Member,
        creating the Guild/Member if they don't exist
        """
