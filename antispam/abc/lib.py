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
import datetime
from typing import Dict, List, Optional, Protocol, Union, runtime_checkable

from antispam.dataclasses import Guild, Member, Message
from antispam.dataclasses.propagate_data import PropagateData
from antispam.libs.shared import SubstituteArgs


@runtime_checkable
class Lib(Protocol):
    """
    A protocol to extend and implement for any libs that wish
    to hook into this package and work natively.

    You also should to subclass :class:`antispam.libs.shared.base.Base`
    as it implements a lot of shared functionality.
    """

    async def check_message_can_be_propagated(self, message) -> PropagateData:
        """
        Given a message from the relevant package,
        run all checks to check if this message should be
        propagated.

        Notes
        -----
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
         has permissions to kick and ban members

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

            `.data` is what gets returned from within propagate itself.
        """
        raise NotImplementedError

    async def create_message(self, message) -> Message:
        """
        Given a message to extract data from, create
        and return a Message class.

        The following should be dumped together as content.
        Order doesn't matter as long as it's consistent.

        - All sticker urls for stickers in the message
        - The actual message content
        - All embeds cast to a string via ``embed_to_string``

        Parameters
        ----------
        message : Union[discord.Message, hikari.messages.Message, pincer.objects.UserMessage]
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

        Warnings
        --------
        This is REQUIRED to be inline with the end options.

        .. code-block:: python
            :linenos:

            if self.handler.options.delete_zero_width_chars:
                content = (
                    content.replace("u200B", "")
                    .replace("u200C", "")
                    .replace("u200D", "")
                    .replace("u200E", "")
                    .replace("u200F", "")
                    .replace("uFEFF", "")
                )
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

        Parameters
        ----------
        guild : Guild
            The guild we wish to send this too
        message : Union[str, discord.Embed, hikari.embeds.Embed, pincer.objects.Embed]
            What to send to the guilds log channel
        delete_after_time : Optional[int]
            How long to delete these messages after
        original_channel : Union[discord.abc.GuildChannel,discord.abc.PrivateChannel,hikari.channels.GuildTextChannel,pincer.objects.Channel]

            Where to send the message assuming this guild has no guild log
            channel already set.
        file
            A file to send

        Notes
        -----
        This should catch any sending errors, log them
        and then proceed to return None.

        If no log channel, don't send anything.
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
        original_message : Union[discord.Message, hikari.messages.Message, pincer.objects.UserMessage]
            Where we get everything from :)
        user_message : Union[str, discord.Embed, hikari.embeds.Embed, pincer.objects.Embed]
            A message to send to the user who is being punished
        guild_message : Union[str, discord.Embed, hikari.embeds.Embed, pincer.objects.Embed]
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
        ------
        MissingGuildPermissions
            I lack perms to carry out this punishment

        Returns
        -------
        bool
            Did the punishment succeed?

        Notes
        -----
        Due to early design decisions, this will only
        ever support kicking or banning. A pain for you and I.
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

        If you need to fetch the channel, cache it please.
        """
        raise NotImplementedError

    async def delete_message(self, message) -> None:
        """
        Given a message, call and handle the relevant
        deletion contexts.

        Parameters
        ----------
        message : Union[discord.Message, hikari.messages.Message, pincer.objects.UserMessage]
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
        Send the given message to the target.

        Parameters
        ----------
        target : Union[discord.abc.Messageable, hikari.channels.TextableChannel]
            Where to send the message.

            Types are unknown for Pincer at this time.
        message : Union[str, discord.Embed, hikari.embeds.Embed, pincer.objects.Embed]
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
        Returns the id of the guild
        this message was sent in.
        """
        raise NotImplementedError

    async def get_channel_id(self, message) -> int:
        """
        Returns the id of the channel
        this message was sent in.
        """
        raise NotImplementedError

    async def get_message_mentions(self, message) -> List[int]:
        """
        Returns all the mention id's from a message.

        This should include:
            - People
            - Roles
            - Channels
        """
        raise NotImplementedError

    async def get_channel_from_message(self, message):
        """
        Given a message, return the channel
        object it was sent in.
        """
        raise NotImplementedError

    async def get_channel_by_id(self, channel_id: int):
        """Returns the given channel object for the id."""
        raise NotImplementedError

    def get_file(self, path: str):
        """Returns a file object for the given path.

        For example, in discord.py this is ``discord.File``
        """
        return NotImplementedError

    async def get_substitute_args(self, message) -> SubstituteArgs:
        """
        Given a message, return the relevant class
        filled with data for usage within ``substitute_args``

        Parameters
        ----------
        message: Union[discord.Message, hikari.messages.Message, pincer.objects.UserMessage]
            The message we are using for creation

        Returns
        -------
        SubstituteArgs
            A dataclass with the relevant data for substitution.
        """
        raise NotImplementedError

    async def lib_embed_as_dict(self, embed) -> Dict:
        """
        Given the relevant Embed object for your
        library, return it in dictionary form.

        Parameters
        ----------
        embed: Union[discord.Embed, hikari.embeds.Embed, pincer.objects.Embed]
            The embed

        Returns
        -------
        dict
            The embed as a dictionary
        """
        raise NotImplementedError

    async def dict_to_lib_embed(self, data: Dict):
        """
        Create an Embed object using a dictionary
        and return that.

        Parameters
        ----------
        data: Dict
            The data to create the embed from

        Returns
        -------
        Union[discord.Embed, hikari.embeds.Embed, pincer.objects.Embed]
            The dictionary as an embed

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

        Notes
        -----
        This is implemented in :class:`antispam.libs.shared.base.Base`
        so assuming you subclass it you don't need to create this.
        """
        raise NotImplementedError

    async def embed_to_string(self, embed) -> str:
        """
        Given an embed, return a string representation.

        This string representation should include the following.
        Ordering does not matter as long as it is consistent.

        - The embeds title
        - The embeds description
        - The embeds footer text
        - The embeds author name
        - All names + values for embed fields

        Parameters
        ----------
        embed : Union[discord.Embed, hikari.embeds.Embed]
            The embed to cast to string

        Returns
        -------
        str
            The embed as a string

        Notes
        -----
        This is implemented in :class:`antispam.libs.shared.base.Base`
        so assuming you subclass it you don't need to create this.
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
        Union[discord.Embed, hikari.embeds.Embed, pincer.objects.Embed]
            The embed

        Notes
        -----
        This is implemented in :class:`antispam.libs.shared.base.Base`
        so assuming you subclass it you don't need to create this.
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

        Notes
        -----
        This is implemented in :class:`antispam.libs.shared.base.Base`
        so assuming you subclass it you don't need to create this.
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

        Notes
        -----
        This is implemented in :class:`antispam.libs.shared.base.Base`
        so assuming you subclass it you don't need to create this.
        """
        raise NotImplementedError

    async def timeout_member(
        self, member, original_message, until: datetime.timedelta
    ) -> None:
        """
        Timeout the given member.

        Parameters
        ----------
        member: Union[discord.Member, hikari.guilds.Member]
            The member to timeout
        original_message
            The message being propagated
        until: datetime.timedelta
            How long to time them out for.

        Raises
        ------
        UnsupportedAction
            Timing out members is not supported.
        MissingGuildPermissions
            Can't time this member out
        """
        raise NotImplementedError

    async def get_member_from_message(self, message):
        """
        Given the message, return the Author's object

        Parameters
        ----------
        message: Union[discord.Message, hikari.messages.Message, pincer.objects.Embed]
            The message to extract it from

        Returns
        -------
        Union[discord.Member, hikari.guilds.Member, ...]
            The member object
        """
        raise NotImplementedError

    async def is_member_currently_timed_out(self, member) -> bool:
        """
        Given the libraries member object,
        return True if they are currently timed
        out or False otherwise.

        Parameters
        ----------
        member: Union[discord.member, hikari.guilds.Member]
            The member to check agaisnt.

        Returns
        -------
        bool
            True if timed out, otherwise False
        """
        raise NotImplementedError

    def is_dm(self, message) -> bool:
        """
        Returns True if this message occurred in a dm, False otherwise.

        Parameters
        ----------
        message
            The discord message this is called on.
        """
        raise NotImplementedError
