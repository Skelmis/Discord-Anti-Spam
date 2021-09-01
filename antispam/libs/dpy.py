import ast
import datetime
import logging
from string import Template
from typing import Union
from unittest.mock import AsyncMock

import discord

from antispam import PropagateFailure
from antispam.abc import Lib
from antispam.dataclasses.propagate_data import PropagateData

log = logging.getLogger(__name__)


# noinspection PyProtocol
class DPY(Lib):
    def __init__(self, handler):
        self.handler = handler

    def substitute_args(
        self,
        message: str,
        original_message: discord.Message,
        warn_count: int,
        kick_count: int,
    ) -> str:
        return Template(message).safe_substitute(
            {
                "MENTIONUSER": original_message.author.mention,
                "USERNAME": original_message.author.display_name,
                "USERID": original_message.author.id,
                "BOTNAME": original_message.guild.me.display_name,
                "BOTID": original_message.guild.me.id,
                "GUILDID": original_message.guild.id,
                "GUILDNAME": original_message.guild.name,
                "TIMESTAMPNOW": datetime.datetime.now().strftime(
                    "%I:%M:%S %p, %d/%m/%Y"
                ),
                "TIMESTAMPTODAY": datetime.datetime.now().strftime("%d/%m/%Y"),
                "WARNCOUNT": warn_count,
                "KICKCOUNT": kick_count,
                "USERAVATAR": original_message.author.avatar_url,
                "BOTAVATAR": original_message.guild.me.avatar_url,
                "GUILDICON": original_message.guild.icon_url,
            }
        )

    def embed_to_string(self, embed: discord.Embed) -> str:
        content = ""
        embed = embed.to_dict()

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

    def dict_to_embed(
        self, data: dict, message: discord.Message, warn_count: int, kick_count: int
    ):
        allowed_avatars = ["$USERAVATAR", "$BOTAVATAR", "$GUILDICON"]

        if "title" in data:
            data["title"] = self.substitute_args(
                data["title"], message, warn_count, kick_count
            )

        if "description" in data:
            data["description"] = self.substitute_args(
                data["description"], message, warn_count, kick_count
            )

        if "footer" in data:
            if "text" in data["footer"]:
                data["footer"]["text"] = self.substitute_args(
                    data["footer"]["text"], message, warn_count, kick_count
                )

            if "icon_url" in data["footer"]:
                if data["footer"]["icon_url"] in allowed_avatars:
                    data["footer"]["icon_url"] = self.substitute_args(
                        data["footer"]["icon_url"], message, warn_count, kick_count
                    )

        if "author" in data:
            # name 'should' be required
            data["author"]["name"] = self.substitute_args(
                data["author"]["name"], message, warn_count, kick_count
            )

            if "icon_url" in data["author"]:
                if data["author"]["icon_url"] in allowed_avatars:
                    data["author"]["icon_url"] = self.substitute_args(
                        data["author"]["icon_url"], message, warn_count, kick_count
                    )

        if "fields" in data:
            for field in data["fields"]:
                name = self.substitute_args(
                    field["name"], message, warn_count, kick_count
                )
                value = self.substitute_args(
                    field["value"], message, warn_count, kick_count
                )
                field["name"] = name
                field["value"] = value

                if "inline" not in field:
                    field["inline"] = True

        if "timestamp" in data:
            data["timestamp"] = message.created_at.isoformat()

        if "colour" in data:
            data["color"] = data["colour"]

        data["type"] = "rich"

        return discord.Embed.from_dict(data)

    def transform_message(
        self,
        item: Union[str, dict],
        message: discord.Message,
        warn_count: int,
        kick_count: int,
    ):
        if isinstance(item, str):
            return self.self.substitute_args(item, message, warn_count, kick_count)

        return self.dict_to_embed(item, message, warn_count, kick_count)

    def visualizer(
        self,
        content: str,
        message: discord.Message,
        warn_count: int = 1,
        kick_count: int = 2,
    ):
        if content.startswith("{"):
            content = ast.literal_eval(content)

        return self.transform_message(content, message, warn_count, kick_count)

    async def check_message_can_be_propagated(
        self, message: discord.Message
    ) -> PropagateData:
        if not isinstance(message, (discord.Message, AsyncMock)):
            raise PropagateFailure(
                data={"status": "Expected message of type discord.Message"}
            )

        # Ensure we only moderate actual guild messages
        if not message.guild:
            log.debug("Message was not in a guild")
            raise PropagateFailure(data={"status": "Ignoring messages from dm's"})

        # The bot is immune to spam
        if message.author.id == self.handler.bot.user.id:
            log.debug("Message was from myself")
            raise PropagateFailure(
                data={"status": "Ignoring messages from myself (the bot)"}
            )

        if isinstance(message.author, discord.User):
            log.warning(f"Given message with an author of type User")

        # Return if ignored bot
        if self.handler.options.ignore_bots and message.author.bot:
            log.debug(f"I ignore bots, and this is a bot message: {message.author.id}")
            raise PropagateFailure(data={"status": "Ignoring messages from bots"})

        # Return if ignored member
        if message.author.id in self.handler.options.ignored_members:
            log.debug(f"The user who sent this message is ignored: {message.author.id}")
            raise PropagateFailure(
                data={"status": f"Ignoring this member: {message.author.id}"}
            )

        # Return if ignored channel
        if (
            message.channel.id in self.handler.options.ignored_channels
            or message.channel.name in self.handler.options.ignored_channels
        ):
            log.debug(f"{message.channel} is ignored")
            raise PropagateFailure(
                data={"status": f"Ignoring this channel: {message.channel.id}"}
            )

        # Return if member has an ignored role
        try:
            user_roles = [role.id for role in message.author.roles]
            user_roles.extend([role.name for role in message.author.roles])
            for item in user_roles:
                if item in self.handler.options.ignored_roles:
                    log.debug(f"{item} is a part of ignored roles")
                    raise PropagateFailure(
                        data={"status": f"Ignoring this role: {item}"}
                    )
        except AttributeError:
            log.warning(
                f"Could not compute ignored_roles for {message.author.name}({message.author.id})"
            )

        # Return if ignored guild
        if message.guild.id in self.handler.options.ignored_guilds:
            log.debug(f"{message.guild.id} is an ignored guild")
            raise PropagateFailure(
                data={"status": f"Ignoring this guild: {message.guild.id}"}
            )

        perms = message.guild.me.guild_permissions
        has_perms = perms.kick_members or perms.ban_members

        return PropagateData(
            guild_id=message.guild.id,
            member_name=message.author.name,
            member_id=message.author.id,
            has_perms_to_make_guild=has_perms,
        )
