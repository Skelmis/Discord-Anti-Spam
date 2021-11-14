"""
The MIT License (MIT)

Copyright (c) 2020-Current Skelmis

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from typing import Protocol, runtime_checkable, Union, Optional, AsyncIterable, List

from antispam.dataclasses import Guild, Member, Message
from antispam.dataclasses.propagate_data import PropagateData
from antispam.enums import ResetType


@runtime_checkable
class Cache(Protocol):
    """A generic Protocol for any Cache to implement"""

    def __init__(self, handler) -> None:
        """Stores the handler for later option usage"""
        self.handler = handler

    async def initialize(self, *args, **kwargs) -> None:
        """
        This method gets called once when the AntiSpamHandler
        init() method gets called to allow for setting up
        connections, etc

        Notes
        -----
        This is not required.
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

    async def delete_guild(self, guild_id: int) -> None:
        """
        Removes a guild from the cache.

        Parameters
        ----------
        guild_id : int
            The id of the guild we wish to remove

        Notes
        -----
        This fails silently.
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

    async def delete_member(self, member_id: int, guild_id: int) -> None:
        """
        Removes a member from the cache.

        Parameters
        ----------
        member_id : int
            The id of the member we wish to remove
        guild_id : int
            The guild this member is in

        Notes
        -----
        This fails silently.
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
        reset_type : ResetType
            An enum denoting the type of reset

        """
        raise NotImplementedError

    async def get_all_guilds(self) -> AsyncIterable[Guild]:
        """
        Returns a generator containing all cached guilds

        Yields
        ------
        Guild
            A generator of all stored guilds
        """

    async def get_all_members(self, guild_id: int) -> AsyncIterable[Member]:
        """
        Fetches all members within a guild and returns
        them within a generator

        Parameters
        ----------
        guild_id : int
            The guild we want members in

        Yields
        ------
        Member
            All members in the given guild

        Raises
        ------
        GuildNotFound
            The given guild was not found
        """

    async def drop(self) -> None:
        """
        Drops the entire cache,
        deleting everything contained within.
        """
        raise NotImplementedError


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

        See Also
        --------
        Should error on the following:
         - If not an instance of the library's message class
         - If in dm's
         - If the message is from yourself (the bot)
         - If ``self.handler.options.ignore_bots`` is ``True`` and the
           message is from a bot
         - If the guild id is in ``self.handler.options.ignored_guilds``
         - If the member id is in ``self.handler.options.ignored_members``
         - If the channel id is in ``self.handler.options.ignored_channels``
         - If any of the member's roles (id) are in ``self.handler.options.ignored_roles``

         ``PropagateData.has_perms_to_make_guild`` should be ``True`` if the member
         has permissions to kick people and ban members

        Parameters
        ----------
        message : Union[discord.Message, hikari.messages.Message, pincer.objects.Embed]
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

    async def substitute_args(
        self, message: str, original_message, warn_count: int, kick_count: int
    ) -> str:
        """
        Given a message, substitute in relevant arguments
        and return a valid string

        Parameters
        ----------
        message : str
            The message to substitute args into
        original_message : Union[discord.Message, hikari.messages.Message, pincer.objects.UserMessage]
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

    async def embed_to_string(self, embed) -> str:
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

    async def dict_to_embed(
        self, data: dict, message, warn_count: int, kick_count: int
    ):
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

        Notes
        -----
        Make sure to deepcopy ``data`` within impl's
        """
        raise NotImplementedError

    async def transform_message(
        self, item: Union[str, dict], message, warn_count: int, kick_count: int
    ):
        """

        Parameters
        ----------
        item : Union[str, dict]
            The data to substitute
        message : Union[discord.Message, hikari.messages.Message, pincer.objects.UserMessage]
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

    async def visualizer(
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

    async def create_message(self, message) -> Message:
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

        Raises
        ------
        InvalidMessage
            If it couldn't create a message,
            I.e message only contained attachments
        """
        raise NotImplementedError

    async def send_guild_log(
        self,
        guild,
        message,
        delete_after_time: Optional[int],
        original_channel,
        file=None,
    ) -> None:
        """
        Sends a message to the guilds log channel

        Notes
        -----
        If no log channel, don't send anything

        Parameters
        ----------
        guild : Guild
            The guild we wish to send this too
        message : Union[str, discord.Embed, hikari.embeds.Embed]
            What to send to the guilds log channel
        delete_after_time : Optional[int]
            How long to delete these messages after
        original_channel : Union[discord.abc.GuildChannel, discord.abc.PrivateChannel, hikari.channels.GuildTextChannel]
            Where to send the message assuming this guild has no guild log
            channel already set.
        file
            A file to send

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
        Supports: kicking, banning

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
        user_delete_after : int, Optional
            An int value denoting the time to
            delete user sent messages after
        channel_delete_after : int, Optional
            An int value denoting the time to
            delete channel sent messages after

        Raises
        ======
        MissingGuildPermissions
            I lack perms to carry out this punishment
        """
        raise NotImplementedError

    async def delete_member_messages(self, member: Member) -> None:
        """
        Given a member, traverse all duplicate messages
        and delete them.

        Parameters
        ----------
        member : Member
            The member whose messages should be deleted

        Notes
        -----
        Just call delete_message on each message
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
        self, target, message, mention: str, delete_after_time: Optional[int] = None
    ) -> None:
        """
        Given a message and target, send
        Parameters
        ----------
        target : Union[discord.abc.Messageable, hikari TODO doc this]
            Where to send the message
        message : Union[str, discord.Embed, hikari.embeds.Embed]
            The message to send
        mention : str
            A string denoting a raw mention of the punished user
        delete_after_time : Optional[int]
            When to delete the message after

        Notes
        -----
        This should implement Options.mention_on_embed
        """
        raise NotImplementedError

    async def get_guild_id(self, message) -> int:
        """
        Returns the guild id of this message
        """
        raise NotImplementedError

    async def get_channel_id(self, message) -> int:
        """
        Returns the channel id of this message
        """
        raise NotImplementedError

    async def get_message_mentions(self, message) -> List[int]:
        """
        Returns all the mentions from a message
        """
        raise NotImplementedError

    async def get_channel_from_message(self, message):
        """Returns the channel for a message"""
        raise NotImplementedError

    async def get_channel_by_id(self, channel_id: int):
        """Returns the given channel for the id"""
        raise NotImplementedError

    def get_file(self, path: str):
        """Returns a discord file object for the given path"""
        return NotImplementedError
