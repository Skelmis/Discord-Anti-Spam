from typing import Protocol, runtime_checkable, List, Union, Optional

from .dataclasses import Guild, Member, Message
from .dataclasses.propagate_data import PropagateData
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

    async def get_all_guilds(self) -> List[Guild]:
        """
        Fetches and guilds a list of all guilds

        Returns
        -------
        List[Guild]
            A list of all stored guilds
        """

    async def get_all_members(self, guild_id: int) -> List[Member]:
        """
        Fetches all members within a guild

        Parameters
        ----------
        guild_id : int
            The guild we want members in

        Returns
        -------
        List[Member]
            All members in the given guild

        Raises
        ------
        GuildNotFound
            The given guild was not found
        """


@runtime_checkable
class Lib(Protocol):
    """
    A protocol to extend and implement for any libs that wish
    to hook into this package and work natively.

    Notes
    -----
    Not public api. For internal usage only.
    """

    async def check_message_can_be_propagated(self, message) -> PropagateData:
        """
        Given a message from the relevant package,
        run all checks to check if this message should be
        propagated.

        Parameters
        ----------
        message : Union[discord.Message, hikari.messages.Message]
            The message to check

        Returns
        -------
        PropagateData
            The data required within propagate

        Raises
        ------
        PropagateFailure
            This raises an error with the `.data` attribute set.
            `.data` is what get returned from within propagate
        """
        raise NotImplementedError

    def substitute_args(
        self, message: str, original_message, warn_count: int, kick_count: int
    ) -> str:
        """
        Given a message, substitute in relevant arguments
        and return a valid string

        Parameters
        ----------
        message : str
            The message to substitute args into
        original_message : Union[discord.Message, hikari.messages.Message]
            The message to extract data from
        warn_count : int
            How many warns this person has
        kick_count : int
            How many kicks this person has


        Returns
        -------
        str
            The message with substituted args
        """
        raise NotImplementedError

    def embed_to_string(self, embed) -> str:
        """
        Given an embed, return a string representation

        Parameters
        ----------
        embed : Union[discord.Embed, hikari.embeds.Embed]
            The embed to cast to string

        Returns
        -------
        str
            The embed as a string
        """
        raise NotImplementedError

    def dict_to_embed(self, data: dict, message, warn_count: int, kick_count: int):
        """

        Parameters
        ----------
        data : dict
            The data to build an embed from
        message : Union[discord.Message, hikari.messages.Message]
            The message to extract data from
        warn_count : int
            How many warns this person has
        kick_count : int
            How many kicks this person has

        Returns
        -------
        Union[discord.Embed, hikari.embeds.Embed]
        """
        raise NotImplementedError

    def transform_message(
        self, item: Union[str, dict], message, warn_count: int, kick_count: int
    ):
        """

        Parameters
        ----------
        item : Union[str, dict]
            The data to substitute
        message : Union[discord.Message, hikari.messages.Message]
            The message to extract data from
        warn_count : int
            How many warns this person has
        kick_count : int
            How many kicks this person has

        Returns
        -------
        Union[str, discord.Embed, hikari.embeds.Embed]
        A template complete message ready for sending

        """
        raise NotImplementedError

    def visualizer(
        self,
        content: str,
        message,
        warn_count: int = 1,
        kick_count: int = 2,
    ):
        """
        Returns a message transformed as if the handler did it

        Parameters
        ----------
        content : Union[str, discord.Embed, hikari.embeds.Embed]
            What to transform
        message : Union[discord.Message, hikari.messages.Message]
            Where to extract our values from
        warn_count : int
            The warns to visualize with
        kick_count : int
            The kicks to visualize with

        Returns
        -------
        Union[str, discord.Embed]
            The transformed content
        """
        raise NotImplementedError

    def create_message(self, message) -> Message:
        """
        Given a message to extract data from, create
        and return a Message class

        Parameters
        ----------
        message : Union[discord.Message, hikari.messages.Message]
            The message to extract data from

        Returns
        -------
        Message
            The flushed out message
        """
        raise NotImplementedError

    async def send_guild_log(self, guild, message, delete_after_time) -> None:
        """
        Sends a message to the guilds log channel

        Parameters
        ----------
        guild : Guild
            The guild we wish to send this too
        message : Union[str, discord.Embed, hikari.embeds.Embed]
            What to send to the guilds log channel
        delete_after_time : Optional[int]
            How long to delete these messages after

        Notes
        -----
        This should catch any sending errors, log them
        and then proceed to return None
        """
        raise NotImplementedError

    async def punish_member(
        self,
        original_message,
        member: Member,
        internal_guild: Guild,
        user_message,
        guild_message,
        is_kick: bool,
        user_delete_after: int = None,
        channel_delete_after: int = None,
    ):
        """
        A generic method to handle multiple methods of punishment for a user.
        Currently supports: kicking, banning
        Parameters
        ----------
        member : Member
            A reference to the member we wish to punish
        internal_guild : Guild
            A reference to the guild this member is in
        original_message : Union[discord.Message, hikari.messages.Message]
            Where we get everything from :)
        user_message : Union[str, discord.Embed, hikari.embeds.Embed]
            A message to send to the user who is being punished
        guild_message : Union[str, discord.Embed, hikari.embeds.Embed]
            A message to send in the guild for whoever is being punished
        is_kick : bool
            Is it a kick? Else ban
        user_delete_after : int, optional
            An int value denoting the time to
            delete user sent messages after
        channel_delete_after : int, optional
            An int value denoting the time to
            delete channel sent messages after
        Raises
        ======
        MissingGuildPerms
            I lack perms to carry out this punishment
        """
        raise NotImplementedError

    async def delete_message(self, message) -> None:
        """
        Given a message, call and handle the relevant
        deletion contexts.

        Parameters
        ----------
        message : Union[discord.Message, hikari.messages.Message]
            The message to delete

        Notes
        -----
        This should handle given errors silently.
        """
        raise NotImplementedError

    async def send_message_to_(
        self, target, message, delete_after_time: Optional[int] = None
    ) -> None:
        """
        Given a message and target, send
        Parameters
        ----------
        target : Union[discord.abc.Messageable, hikari TODO doc this]
            Where to send the message
        message : Union[str, discord.Embed, hikari.embeds.Embed]
            The message to send
        delete_after_time : Optional[int]
            When to delete the message after
        """