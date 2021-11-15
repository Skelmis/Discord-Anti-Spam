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
import ast
import asyncio
import datetime
import logging
from copy import deepcopy
from string import Template
from typing import Optional, Union, Dict
from unittest.mock import AsyncMock

import hikari.errors
from hikari import (
    messages,
    guilds,
    embeds,
    GuildTextChannel,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    RateLimitTooLongError,
    InternalServerError,
    Permissions,
)

from antispam import (
    AntiSpamHandler,
    PropagateFailure,
    LogicError,
    MissingGuildPermissions,
)

from antispam.abc import Lib
from antispam.dataclasses import Member, Guild, Message
from antispam.dataclasses.propagate_data import PropagateData

log = logging.getLogger(__name__)


# noinspection DuplicatedCode,PyProtocol
class Hikari(Lib):
    async def send_message_to_(
        self, target, message, mention: str, delete_after_time: Optional[int] = None
    ) -> None:  # pragma: no cover
        if isinstance(message, hikari.Embed):
            m = await target.send(
                embed=message,
            )
        else:
            m = await target.send(
                message,
            )

        if delete_after_time:
            await asyncio.sleep(delete_after_time)
            await m.delete()

    def __init__(self, handler: AntiSpamHandler):
        self.handler = handler

    async def get_guild_id(self, message: messages.Message) -> int:  # pragma: no cover
        return message.guild_id

    async def get_channel_id(
        self, message: messages.Message
    ) -> int:  # pragma: no cover
        return message.channel_id

    async def get_channel_from_message(
        self, message: messages.Message
    ):  # pragma: no cover
        return await self.handler.bot.rest.fetch_channel(message.channel_id)

    async def get_channel_by_id(self, channel_id: int):  # pragma: no cover
        return await self.handler.bot.rest.fetch_channel(channel_id)

    async def check_message_can_be_propagated(
        self, message: messages.Message
    ) -> PropagateData:
        if not isinstance(message, (messages.Message, AsyncMock)):
            raise PropagateFailure(
                data={"status": "Expected message of type messages.Message"}
            )

        # Ensure we only moderate actual guild messages
        if not message.guild_id:
            log.debug(
                "Message(id=%s) from Member(id=%s) was not in a guild",
                message.id,
                message.author.id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from dm's"})

        # The bot is immune to spam
        if message.author.id == self.handler.bot.get_me().id:
            log.debug("Message(id=%s) was from myself", message.id)
            raise PropagateFailure(
                data={"status": "Ignoring messages from myself (the bot)"}
            )

        guild: guilds.Guild = self.handler.bot.cache.get_guild(message.guild_id)
        member: guilds.Member = guild.get_member(message.author.id)

        if not member:
            log.error(
                "Idk how to fetch members, so this is returning since "
                "cache lookup failed. Please open a github issue."
            )
            raise PropagateFailure(
                data={
                    "status": "Idk how to fetch members, so this is returning since "
                    "cache lookup failed. Please open a github issue."
                }
            )

        # Return if ignored bot
        if self.handler.options.ignore_bots and message.author.is_bot:
            log.debug(
                "I ignore bots, and this is a bot message with author(id=%s)",
                message.author.id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from bots"})

        # Return if ignored guild
        if message.guild_id in self.handler.options.ignored_guilds:
            log.debug("Ignored Guild(id=%s)", message.guild.id)
            raise PropagateFailure(
                data={"status": f"Ignoring this guild: {message.guild_id}"}
            )

        # Return if ignored member
        if message.author.id in self.handler.options.ignored_members:
            log.debug(
                "The Member(id=%s) who sent this message is ignored", message.author.id
            )
            raise PropagateFailure(
                data={"status": f"Ignoring this member: {message.author.id}"}
            )

        # Return if ignored channel
        channel = await message.fetch_channel()
        if (
            message.channel_id in self.handler.options.ignored_channels
            or channel.name in self.handler.options.ignored_channels
        ):
            log.debug("channel(id=%s) is ignored", channel.channel)
            raise PropagateFailure(
                data={"status": f"Ignoring this channel: {message.channel_id}"}
            )

        # Return if member has an ignored role
        try:
            roles = await member.fetch_roles()
            user_roles = list(member.role_ids)
            user_roles.extend([role.name for role in roles])
            for item in user_roles:
                if item in self.handler.options.ignored_roles:
                    log.debug("role(%s) is a part of ignored roles", item)
                    raise PropagateFailure(
                        data={"status": f"Ignoring this role: {item}"}
                    )
        except AttributeError:
            log.warning(
                "Could not compute ignored_roles for %s(%s)",
                message.author.username,
                message.author.id,
            )

        perms: Permissions = await self._get_perms(guild.get_my_member())
        has_perms = bool(perms.KICK_MEMBERS and perms.BAN_MEMBERS)

        return PropagateData(
            guild_id=message.guild_id,
            member_name=message.author.username,
            member_id=message.author.id,
            has_perms_to_make_guild=has_perms,
        )

    async def _get_perms(self, member: guilds.Member) -> Permissions:
        roles = await member.fetch_roles()

        perms = Permissions.NONE

        for role in roles:
            perms |= role.permissions

        return perms

    async def substitute_args(
        self,
        message: str,
        original_message: messages.Message,
        warn_count: int,
        kick_count: int,
    ) -> str:
        guild = self.handler.bot.cache.get_guild(original_message.guild_id)
        me: guilds.Member = guild.get_my_member()
        return Template(message).safe_substitute(
            {
                "MENTIONMEMBER": original_message.author.mention,
                "MEMBERNAME": original_message.author.username,
                "MEMBERID": original_message.author.id,
                "BOTNAME": me.username,
                "BOTID": me.id,
                "GUILDID": original_message.guild_id,
                "GUILDNAME": guild.name,
                "TIMESTAMPNOW": datetime.datetime.now().strftime(
                    "%I:%M:%S %p, %d/%m/%Y"
                ),
                "TIMESTAMPTODAY": datetime.datetime.now().strftime("%d/%m/%Y"),
                "WARNCOUNT": warn_count,
                "KICKCOUNT": kick_count,
                "MEMBERAVATAR": original_message.author.avatar_url,
                "BOTAVATAR": me.avatar_url,
                "GUILDICON": guild.icon_url,
            }
        )

    async def embed_to_string(self, embed_obj: embeds.Embed) -> str:
        content = ""
        embed: Dict = self.handler.bot.entity_factory.serialize_embed(embed_obj)

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
        self, data: dict, message: messages.Message, warn_count: int, kick_count: int
    ):
        allowed_avatars = ["$MEMBERAVATAR", "$BOTAVATAR", "$GUILDICON"]
        data: dict = deepcopy(data)

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

        if "timestamp" in data:
            data["timestamp"] = message.created_at.isoformat()

        if "colour" in data:
            data["color"] = data["colour"]

        data["type"] = "rich"

        return self.handler.bot.entity_factory.deserialize_embed(data)

    async def transform_message(
        self,
        item: Union[str, dict],
        message: messages.Message,
        warn_count: int,
        kick_count: int,
    ):
        if isinstance(item, str):
            return await self.substitute_args(item, message, warn_count, kick_count)

        return await self.dict_to_embed(item, message, warn_count, kick_count)

    async def visualizer(
        self,
        content: str,
        message: messages.Message,
        warn_count: int = 1,
        kick_count: int = 2,
    ):
        if content.startswith("{"):
            content = ast.literal_eval(content)

        return await self.transform_message(content, message, warn_count, kick_count)

    async def create_message(self, message: messages.Message) -> Message:
        log.debug(
            "Attempting to create a new message for author(id=%s) in Guild(%s)",
            message.author.id,
            message.guild_id,
        )
        if not bool(message.content and message.content.strip()):
            if not message.embeds:
                raise LogicError

            embed: embeds.Embed = message.embeds[0]
            if not isinstance(embed, embeds.Embed):
                raise LogicError

            content = await self.embed_to_string(embed)
        else:
            content = message.content

        if self.handler.options.delete_zero_width_chars:
            content = (
                content.replace("u200B", "")
                .replace("u200C", "")
                .replace("u200D", "")
                .replace("u200E", "")
                .replace("u200F", "")
                .replace("uFEFF", "")
            )

        return Message(
            id=message.id,
            channel_id=message.channel_id,
            guild_id=message.guild_id,
            author_id=message.author.id,
            content=content,
        )

    async def send_guild_log(
        self,
        guild: Guild,
        message: Union[embeds.Embed, str],
        delete_after_time: Optional[int],
        original_channel: GuildTextChannel,
        file=None,
    ) -> None:  # pragma: no cover
        try:
            if not guild.log_channel_id:
                log.debug(
                    "Guild(id=%s) has no log channel set, not sending anything",
                    guild.id,
                )
                return

            channel = guild.log_channel_id

            channel = await self.handler.bot.rest.fetch_channel(channel)

            if isinstance(message, str):
                m = await channel.send(message, attachment=file)
            else:
                m = await channel.send(embed=message, attachment=file)

            if delete_after_time:
                await asyncio.sleep(delete_after_time)
                await m.delete()

            log.debug("Sent message to log channel in Guild(id=%s)", guild.id)
        except (
            UnauthorizedError,
            ForbiddenError,
            NotFoundError,
            RateLimitTooLongError,
            InternalServerError,
        ):
            log.error(
                "Failed to send log message in Guild(id=%s). hikari.send_guild_log()",
                guild.id,
            )

    async def punish_member(
        self,
        original_message: messages.Message,
        member: Member,
        internal_guild: Guild,
        user_message,
        guild_message,
        is_kick: bool,
        user_delete_after: int = None,
        channel_delete_after: int = None,
    ):  # pragma: no cover
        guild = self.handler.bot.cache.get_guild(original_message.guild_id)
        author = original_message.author
        channel = await self.handler.bot.rest.fetch_channel(original_message.channel_id)

        # Check we have perms to punish
        perms = await self._get_perms(guild.get_my_member())
        if not perms.KICK_MEMBERS and is_kick:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need kick perms to punish someone in {guild.name}"
            )

        elif not perms.BAN_MEMBERS and not is_kick:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need ban perms to punish someone in {guild.name}"
            )

        # We also check they don't own the guild, since ya know...
        elif guild.owner_id == member.id:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I cannot punish {author.username}({author.id}) "
                f"because they own this guild. ({guild.name})"
            )

        sent_message: Optional[messages.Message] = None
        try:
            if isinstance(user_message, embeds.Embed):
                sent_message = await author.send(embed=user_message)
            else:
                sent_message = await author.send(user_message)

            if user_delete_after:
                await asyncio.sleep(user_delete_after)
                await sent_message.delete()

        except InternalServerError:
            await self.send_guild_log(
                guild=internal_guild,
                message=f"Sending a message to {author.mention} about their {'kick' if is_kick else 'ban'} failed.",
                delete_after_time=channel_delete_after,
                original_channel=channel,
            )
            log.warning(
                f"Failed to message Member(id=%s) about {'kick' if is_kick else 'ban'}",
                author.id,
            )

        # Even if we can't tell them they are being punished
        # We still need to punish them, so try that
        try:
            if is_kick:
                await guild.kick(
                    author, reason="Automated punishment from DPY Anti-Spam."
                )
                log.info("Kicked Member(id=%s)", member.id)
            else:
                await guild.ban(
                    author, reason="Automated punishment from DPY Anti-Spam."
                )
                log.info("Banned Member(id=%s)", member.id)

        except InternalServerError:
            member._in_guild = True
            member.kick_count -= 1
            await self.send_guild_log(
                guild=internal_guild,
                message=f"An error occurred trying to {'kick' if is_kick else 'ban'}: <@{member.id}>",
                delete_after_time=channel_delete_after,
                original_channel=channel,
            )
            log.warning(
                "An error occurred trying to %s: Member(id=%s)",
                {"kick" if is_kick else "ban"},
                member.id,
            )
            if sent_message is not None:
                if is_kick:
                    user_failed_message = await self.transform_message(
                        self.handler.options.member_failed_kick_message,
                        original_message,
                        member.warn_count,
                        member.kick_count,
                    )
                else:
                    user_failed_message = await self.transform_message(
                        self.handler.options.member_failed_ban_message,
                        original_message,
                        member.warn_count,
                        member.kick_count,
                    )

                await self.send_guild_log(
                    internal_guild, user_failed_message, channel_delete_after, channel
                )
                await sent_message.delete()

        else:
            await self.send_guild_log(
                guild=internal_guild,
                message=guild_message,
                delete_after_time=channel_delete_after,
                original_channel=channel,
            )

        member._in_guild = True
        await self.handler.cache.set_member(member)

    async def delete_member_messages(self, member: Member) -> None:  # pragma: no cover
        log.debug(
            "Attempting to delete all duplicate messages for Member(id=%s) in Guild(%s)",
            member.id,
            member.guild_id,
        )
        bot = self.handler.bot
        channels = {}
        for message in member.messages:
            if message.is_duplicate:
                # cache channel for further fetches
                if message.channel_id not in channels:
                    channel: GuildTextChannel = await bot.rest.fetch_channel(
                        message.channel_id
                    )

                    channels[message.channel_id] = channel
                else:
                    channel = channels[message.channel_id]

                try:
                    actual_message = await channel.fetch_message(message.id)
                    await self.delete_message(actual_message)
                except hikari.errors.NotFoundError:
                    continue

    async def delete_message(
        self, message: messages.Message
    ) -> None:  # pragma: no cover
        try:
            await message.delete()
            log.debug("Deleted message: %s", message.id)
        except (NotFoundError, ForbiddenError):
            # Failed to delete message
            log.warning(
                "Failed to delete message %s in Guild(id=%s). NotFoundError | ForbiddenError",
                message.id,
                message.guild_id,
            )

    async def get_message_mentions(self, message: messages.Message):  # pragma: no cover
        data = [message.mentions.user_ids]
        data.extend(role for role in message.mentions.role_ids)
        data.extend(channel for channel in message.mentions.channels_ids)
        return data

    def get_file(self, path: str):  # pragma: no cover
        return hikari.File(path)
