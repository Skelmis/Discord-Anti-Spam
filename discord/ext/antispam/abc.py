from typing import Protocol, runtime_checkable

from .dataclasses import Guild, Member, Message
from .enums import ResetType
from .enums.state import ASHEnum


@runtime_checkable
class Cache(Protocol):
    """A generic Protocol for any Cache to implement"""

    def __init__(self, handler) -> None:
        """Stores the handler for later option usage"""
        self.handler = handler

    async def initialize(self, *args, **kwargs) -> None:
        """
        This method gets called once when the AntiSpamHandler
        first loads so that you can do any async initialization
        you need to do before the cache gets used
        """
        pass

    async def get_guild(self, guild_id: int) -> Guild:
        """Fetch a Guild dataclass populated with members

        Parameters
        ----------
        guild_id : int
            The id of the Guild to retrieve from cache

        Raises
        ------
        GuildNotFound
            A Guild could not be found in the cache
            with the given id
        """
        raise NotImplementedError

    async def set_guild(self, guild: Guild) -> None:
        """
        Stores a Guild in the cache

        This is essentially a UPSERT operation

        Parameters
        ----------
        guild : Guild
            The Guild that needs to be stored
        """
        raise NotImplementedError

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        """Fetch a Member dataclass populated with messages

        Parameters
        ----------
        member_id : int
            The id of the member to fetch from cache
        guild_id : int
            The id of the guild this member is associated with

        Raises
        ------
        MemberNotFound
            This Member could not be found on the associated
            Guild within the internal cache
        GuildNotFound
            The relevant guild could not be found
        """
        raise NotImplementedError

    async def set_member(self, member: Member) -> None:
        """
        Stores a Member internally and attaches them
        to a Guild, creating the Guild silently if required

        Essentially an UPSERT operation

        Parameters
        ----------
        member : Member
            The Member we want to cache
        """
        raise NotImplementedError

    async def add_message(self, message: Message) -> None:
        """
        Adds a Message to the relevant Member,
        creating the Guild/Member if they don't exist

        Parameters
        ----------
        message : Message
            The Message to add to the internal cache

        Notes
        -----
        This should silently create any Guild's/Member's
        required to fulfil this transaction
        """
        raise NotImplementedError

    async def reset_member_count(
        self, member_id: int, guild_id: int, reset_type: ResetType
    ) -> None:
        """
        Reset the chosen enum type back to the default value

        Parameters
        ----------
        member_id : int
            The Member to reset
        guild_id : int
            The guild this member is in
        reset_type : ASHEnum
            An enum denoting the type of reset

        """
        raise NotImplementedError

    # TODO Implement Member count resets
    # TODO Implement a way to get all Guilds / Members
