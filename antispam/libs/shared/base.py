from __future__ import annotations

import ast
import logging
from copy import deepcopy
from string import Template
from typing import Dict, Union, TYPE_CHECKING, Optional, cast, List
from unittest.mock import AsyncMock

from antispam import PropagateFailure, GuildNotFound
from antispam.dataclasses.propagate_data import PropagateData
from antispam.libs.shared import SubstituteArgs

if TYPE_CHECKING:
    from antispam import AntiSpamHandler

log = logging.getLogger(__name__)


class Base:
    """A base Library feature class which implements shared functionality."""

    def __init__(self, handler: AntiSpamHandler):
        self.handler = handler

    def check_if_message_is_from_a_bot(self, message) -> bool:
        """Given a message object, return if it was sent by a bot

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        bool
            True if the message is from a bot else false

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def does_author_have_kick_and_ban_perms(self, message) -> bool:
        """Given a message object, return if the
        author has both kick and ban perms

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        bool
            True if the author has them else False

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_guild_id_from_message(self, message) -> Optional[int]:
        """Given a message object, return the guilds id.

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        int
            The guild's id
        None
            This message is not in a guild

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_author_id_from_message(self, message) -> int:
        """Given a message object, return the authors id.

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        int
            The author's id

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_author_name_from_message(self, message) -> str:
        """Given a message object, return the authors name.

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        str
            The author's name

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_bot_id_from_message(self, message) -> int:
        """Given a message object, return this bots id.

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        int
            The bot's id

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_message_id_from_message(self, message) -> int:
        """Given a message object, return the message id.

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        int
            The message id

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_channel_id_from_message(self, message) -> int:
        """Given a message object, return the channel id.

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        int
            The channel id

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_role_ids_for_message_author(self, message) -> List[int]:
        """Given a message object, return the role ids for the author

        Parameters
        ----------
        message
            Your libraries message object

        Returns
        -------
        List[int]
            A list of role ids, empty list if you can't get any

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    def get_expected_message_type(self):
        """Return the expected type of your libraries message.

        I.e. discord.Message

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def get_substitute_args(self, message) -> SubstituteArgs:
        """

        Parameters
        ----------
        message
            Message used to create SubstituteArgs

        Returns
        -------
        SubstituteArgs

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def lib_embed_as_dict(self, embed) -> Dict:
        """
        Parameters
        ----------
        embed
            Your libraries embed object.

        Returns
        -------
        dict
            The embed in dict form

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def dict_to_lib_embed(self, data: Dict):
        """
        Parameters
        ----------
        data: dict
            The embed as a dictionary, used
            to build a an embed object for your library.

        Returns
        -------
        Any
            Your libraries embed object.

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def substitute_args(
        self,
        content,
        message,
        warn_count: int,
        kick_count: int,
    ) -> str:
        substitute_args: SubstituteArgs = await self.get_substitute_args(message)
        log.debug(
            "Substituting arguments on Message(id=%s) for Member(id=%s)",
            message.id,
            substitute_args.member_id,
        )

        return Template(content).safe_substitute(
            {
                "MEMBERID": substitute_args.member_id,
                "MEMBERNAME": substitute_args.member_name,
                "MEMBERAVATAR": substitute_args.member_avatar,
                "MENTIONMEMBER": substitute_args.mention_member,
                "BOTID": substitute_args.bot_id,
                "BOTNAME": substitute_args.bot_name,
                "BOTAVATAR": substitute_args.bot_avatar,
                "MENTIONBOT": substitute_args.mention_bot,
                "GUILDID": substitute_args.guild_id,
                "GUILDNAME": substitute_args.guild_name,
                "GUILDICON": substitute_args.guild_icon,
                "TIMESTAMPNOW": substitute_args.timestamp_now,
                "TIMESTAMPTODAY": substitute_args.timestamp_today,
                "WARNCOUNT": warn_count,
                "KICKCOUNT": kick_count,
            }
        )

    async def embed_to_string(self, embed) -> str:
        content = ""
        embed = await self.lib_embed_as_dict(embed)
        log.debug("Converting the following to a string, %s", embed)

        if "title" in embed:
            content += f"{embed['title']}\n"

        if "description" in embed:
            content += f"{embed['description']}\n"

        if "footer" in embed:
            if "text" in embed["footer"]:
                content += f"{embed['footer']['text']}\n"

        if "author" in embed:
            content += f"{embed['author']['name']}\n"

        if "fields" in embed:
            for field in embed["fields"]:
                content += f"{field['name']}\n{field['value']}\n"

        return content

    async def dict_to_embed(
        self, data: dict, message, warn_count: int, kick_count: int
    ):
        allowed_avatars = ["$MEMBERAVATAR", "$BOTAVATAR", "$GUILDICON"]
        data: dict = deepcopy(data)
        log.debug("Converting the following to an embed, %s", data)

        if "title" in data:
            data["title"] = await self.substitute_args(
                data["title"], message, warn_count, kick_count
            )

        if "description" in data:
            data["description"] = await self.substitute_args(
                data["description"], message, warn_count, kick_count
            )

        if "footer" in data:
            if "text" in data["footer"]:
                data["footer"]["text"] = await self.substitute_args(
                    data["footer"]["text"], message, warn_count, kick_count
                )

            if "icon_url" in data["footer"]:
                if data["footer"]["icon_url"] in allowed_avatars:
                    data["footer"]["icon_url"] = await self.substitute_args(
                        data["footer"]["icon_url"], message, warn_count, kick_count
                    )

        if "author" in data:
            # name 'should' be required
            data["author"]["name"] = await self.substitute_args(
                data["author"]["name"], message, warn_count, kick_count
            )

            if "icon_url" in data["author"]:
                if data["author"]["icon_url"] in allowed_avatars:
                    data["author"]["icon_url"] = await self.substitute_args(
                        data["author"]["icon_url"], message, warn_count, kick_count
                    )

        if "fields" in data:
            for field in data["fields"]:
                name = await self.substitute_args(
                    field["name"], message, warn_count, kick_count
                )
                value = await self.substitute_args(
                    field["value"], message, warn_count, kick_count
                )
                field["name"] = name
                field["value"] = value

                if "inline" not in field:
                    field["inline"] = True

        if "timestamp" in data:  # pragma: no cover
            data["timestamp"] = message.created_at.isoformat()

        if "colour" in data:
            data["color"] = data["colour"]

        data["type"] = "rich"

        return await self.dict_to_lib_embed(data)

    async def transform_message(
        self,
        content: Union[str, dict],
        message,
        warn_count: int,
        kick_count: int,
    ):
        if isinstance(content, str):
            return await self.substitute_args(content, message, warn_count, kick_count)

        return await self.dict_to_embed(content, message, warn_count, kick_count)

    async def visualizer(
        self,
        content: str,
        message,
        warn_count: int = 1,
        kick_count: int = 2,
    ):
        log.debug("Attempting to visualize %s", content)
        if content.startswith("{"):
            content = ast.literal_eval(content)

        return await self.transform_message(content, message, warn_count, kick_count)

    async def check_message_can_be_propagated(self, message) -> PropagateData:
        message_type = self.get_expected_message_type()
        if not isinstance(message, (message_type, AsyncMock)):
            raise PropagateFailure(
                data={
                    "status": f"Expected message of type {message_type.__class__.__name__}"
                }
            )

        guild_id = self.get_guild_id_from_message(message)
        author_id = self.get_author_id_from_message(message)
        message_id = self.get_message_id_from_message(message)

        # Ensure we only moderate actual guild messages
        if not guild_id:
            log.debug(
                "Message(id=%s) from Member(id=%s) was not in a guild",
                message_id,
                author_id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from dm's"})

        channel_id = self.get_channel_id_from_message(message)
        author_name = self.get_author_name_from_message(message)
        bot_id = self.get_bot_id_from_message(message)
        is_bot_message = self.check_if_message_is_from_a_bot(message)
        guild_id = cast(int, guild_id)

        # The bot is immune to spam
        if author_id == bot_id:
            log.debug("Message(id=%s) was from myself", message_id)
            raise PropagateFailure(
                data={"status": "Ignoring messages from myself (the bot)"}
            )

        try:
            guild_options = await self.handler.get_guild_options(guild_id)
        except GuildNotFound:
            from antispam import Options

            guild_options = Options()

        # Return if ignored bot
        if (
            self.handler.options.ignore_bots or guild_options.ignore_bots
        ) and is_bot_message:
            log.debug(
                "I ignore bots, and this is a bot message with author(id=%s)",
                author_id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from bots"})

        # Return if ignored guild
        if guild_id in self.handler.options.ignored_guilds:
            log.debug("Ignored Guild(id=%s)", guild_id)
            raise PropagateFailure(data={"status": f"Ignoring this guild: {guild_id}"})

        # Return if ignored member
        if (
            author_id in self.handler.options.ignored_members
            or author_id in guild_options.ignored_members
        ):
            log.debug("The Member(id=%s) who sent this message is ignored", author_id)
            raise PropagateFailure(
                data={"status": f"Ignoring this member: {author_id}"}
            )

        # Return if ignored channel
        if channel_id in self.handler.options.ignored_channels:
            log.debug("channel(id=%s) is ignored", channel_id)
            raise PropagateFailure(
                data={"status": f"Ignoring this channel: {channel_id}"}
            )

        # Return if member has an ignored role
        user_roles = self.get_role_ids_for_message_author(message)
        for item in user_roles:
            if item in self.handler.options.ignored_roles:
                log.debug(
                    "Ignoring Member(id=%s) as they have an ignored Role(id%s)",
                    author_id,
                    item,
                )
                raise PropagateFailure(data={"status": f"Ignoring this role: {item}"})

        has_perms = await self.does_author_have_kick_and_ban_perms(message)

        return PropagateData(
            guild_id=guild_id,
            member_name=author_name,
            member_id=author_id,
            has_perms_to_make_guild=has_perms,
        )
