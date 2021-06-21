from typing import Protocol, runtime_checkable

from .dataclasses import Guild, Member, Message

# TODO These imports might complain about being circles


@runtime_checkable
class Cache(Protocol):
    """A generic Protocol for any Cache to implement"""

    async def initialize(self, *args, **kwargs) -> None:
        """
        This method gets called once when the AntiSpamHandler
        first loads so that you can do any async initialization
        you need to do before the cache gets useds
        """

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

    async def set_guild(self, guild: Guild) -> None:
        """
        Stores a Guild in the cache

        This is essentially a UPSERT operation

        Parameters
        ----------
        guild : Guild
            The Guild that needs to be stored
        """

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
        """

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

    # TODO Implement Member count resets
