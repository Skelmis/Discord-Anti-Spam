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
import asyncio
import datetime
import logging
from typing import Dict, Optional, Union
from unittest.mock import AsyncMock

import hikari.errors
from hikari import (
    ForbiddenError,
    GuildTextChannel,
    InternalServerError,
    NotFoundError,
    Permissions,
    RateLimitTooLongError,
    UnauthorizedError,
    embeds,
    guilds,
    messages,
)

from antispam import (
    AntiSpamHandler,
    InvalidMessage,
    LogicError,
    MissingGuildPermissions,
    PropagateFailure,
)
from antispam.abc import Lib
from antispam.dataclasses import Guild, Member, Message
from antispam.dataclasses.propagate_data import PropagateData
from antispam.deprecation import mark_deprecated
from antispam.libs.shared import Base, SubstituteArgs

log = logging.getLogger(__name__)


class Hikari(Base, Lib):
    def __init__(self, handler: AntiSpamHandler):
        self.handler = handler

    async def get_substitute_args(self, message) -> SubstituteArgs:
        guild = self.handler.bot.cache.get_guild(message.guild_id)
        me: guilds.Member = guild.get_my_member()

        return SubstituteArgs(
            bot_id=me.id,
            bot_name=me.name,
            bot_avatar=str(me.avatar_url),
            guild_id=message.guild_id,
            guild_icon=guild.icon_url,
            guild_name=message.guild.name,
            member_id=message.author.id,
            member_name=message.author.username,
            member_avatar=str(message.author.avatar_url),
        )

    async def lib_embed_as_dict(self, embed) -> Dict:
        return self.handler.bot.entity_factory.serialize_embed(embed)

    async def dict_to_lib_embed(self, data: Dict):
        return self.handler.bot.entity_factory.deserialize_embed(data)

    async def get_member_from_message(self, message: messages.Message):
        guild: guilds.Guild = self.handler.bot.cache.get_guild(message.guild_id)
        return guild.get_member(message.author.id)

    async def send_message_to_(
        self, target, message, mention: str, delete_after_time: Optional[int] = None
    ) -> None:  # pragma: no cover
        if isinstance(message, hikari.Embed):
            content = None
            if self.handler.options.mention_on_embed:
                content = mention
            m = await target.send(
                content=content,
                embed=message,
            )
        else:
            m = await target.send(
                message,
            )

        if delete_after_time:
            await asyncio.sleep(delete_after_time)
            await m.delete()

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
        if message.channel_id in self.handler.options.ignored_channels:
            log.debug("channel(id=%s) is ignored", channel.id)
            raise PropagateFailure(
                data={"status": f"Ignoring this channel: {message.channel_id}"}
            )

        # Return if member has an ignored role
        try:
            roles = await member.fetch_roles()
            user_roles = list(member.role_ids)
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

    async def create_message(self, message: messages.Message) -> Message:
        log.debug(
            "Attempting to create a new message for author(id=%s) in Guild(%s)",
            message.author.id,
            message.guild_id,
        )
        content = ""
        if message.stickers:
            # 'sticker' names should be unique..
            all_stickers = "|".join(s.name for s in message.stickers)
            content += all_stickers

        if not bool(message.content and message.content.strip()):
            if not message.embeds and not message.attachments:
                raise LogicError

            if not message.embeds:
                # We dont check attachments lol
                raise InvalidMessage

            for embed in message.embeds:
                if not isinstance(embed, embeds.Embed):
                    raise LogicError

                content += await self.embed_to_string(embed)
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

            channel_id = guild.log_channel_id
            if isinstance(message, str):
                m = await self.handler.bot.rest.send_message(
                    channel_id, message, attachment=file
                )
            else:
                m = await self.handler.bot.rest.send_message(
                    channel_id, embed=message, attachment=file
                )

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
            member.internal_is_in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need kick perms to punish someone in {guild.name}"
            )

        elif not perms.BAN_MEMBERS and not is_kick:
            member.internal_is_in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need ban perms to punish someone in {guild.name}"
            )

        # We also check they don't own the guild, since ya know...
        elif guild.owner_id == member.id:
            member.internal_is_in_guild = True
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
        _success = True
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
            _success = False
            member.internal_is_in_guild = True
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

        member.internal_is_in_guild = True
        await self.handler.cache.set_member(member)
        return _success

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

    async def timeout_member(
        self,
        member: guilds.Member,
        original_message: messages.Message,
        until: datetime.timedelta,
    ) -> None:
        guild: guilds.Guild = self.handler.bot.cache.get_guild(member.guild_id)
        perms = await self._get_perms(guild.get_my_member())  # type: ignore
        if not perms.MODERATE_MEMBERS:
            raise MissingGuildPermissions(
                "MODERATE_MEMBERS is required to timeout members.\n"
                f"Tried timing out Member(id={member.id}) in Guild(id={member.guild_id})"
            )

        internal_guild: Guild = await self.handler.cache.get_guild(member.guild_id)

        time_now = datetime.datetime.utcnow() + until
        await member.edit(
            communication_disabled_until=time_now, reason="Automated timeout from Discord-Anti-Spam"  # type: ignore
        )

    async def is_member_currently_timed_out(self, member: guilds.Member) -> bool:
        return bool(member.raw_communication_disabled_until)

    def is_dm(self, message: messages.Message) -> bool:
        return not bool(message.guild_id)
