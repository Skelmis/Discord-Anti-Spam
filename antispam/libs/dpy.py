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
from __future__ import annotations

import datetime
import logging
from typing import Dict, Optional, Union, List
from unittest.mock import AsyncMock

from antispam.deprecation import mark_deprecated
from antispam.libs.shared import Base, SubstituteArgs

try:
    import discord
except ModuleNotFoundError:  # pragma: no cover
    import disnake as discord

from antispam import (
    InvalidMessage,
    MissingGuildPermissions,
    PropagateFailure,
    UnsupportedAction,
)
from antispam.abc import Lib
from antispam.dataclasses import Guild, Member, Message
from antispam.dataclasses.propagate_data import PropagateData

log = logging.getLogger(__name__)


class DPY(Base, Lib):
    def __init__(self, handler):
        self.handler = handler
        self.bot = self.handler.bot

    def get_expected_message_type(self):
        return discord.Message

    def get_author_id_from_message(self, message) -> int:
        return message.author.id

    def get_author_name_from_message(self, message) -> str:
        return message.author.name

    def get_bot_id_from_message(self, message) -> int:
        return self.handler.bot.user.id

    def get_channel_id_from_message(self, message) -> int:
        return message.channel.id

    def get_message_id_from_message(self, message) -> int:
        return message.id

    def get_guild_id_from_message(self, message) -> Optional[int]:
        if message.guild:
            return message.guild.id

        return None

    def get_role_ids_for_message_author(self, message) -> List[int]:
        try:
            return [role.id for role in message.author.roles]
        except AttributeError:
            return []

    def check_if_message_is_from_a_bot(self, message) -> bool:
        return message.author.bot

    async def does_author_have_kick_and_ban_perms(self, message) -> bool:
        perms = message.guild.me.guild_permissions
        return perms.kick_members and perms.ban_members

    def get_file(self, path: str):  # pragma: no cover
        return discord.File(path)

    async def lib_embed_as_dict(self, embed: discord.Embed) -> Dict:
        return embed.to_dict()

    async def get_channel_from_message(
        self,
        message: discord.Message,
    ):  # pragma: no cover
        return message.channel

    async def get_message_mentions(self, message: discord.Message):  # pragma: no cover
        return message.mentions

    async def get_member_from_message(self, message):
        return message.author

    async def get_channel_by_id(self, channel_id: int):  # pragma: no cover
        channel = self.bot.get_channel(channel_id)
        if not channel:
            channel = await self.bot.fetch_channel(channel_id)

        return channel

    async def dict_to_lib_embed(self, data: Dict) -> discord.Embed:
        return discord.Embed.from_dict(data)

    async def get_guild_id(self, message: discord.Message) -> int:
        return message.guild.id

    async def get_channel_id(self, message: discord.Message) -> int:
        return message.channel.id

    async def get_substitute_args(
        self, message: discord.Message
    ) -> SubstituteArgs:  # pragma: no cover
        version = int(discord.__version__.split(".")[0])
        if version >= 2:
            member_avatar = str(message.author.display_avatar)
            bot_avatar = str(message.guild.me.display_avatar)

            guild_icon = message.guild.icon
            guild_icon = guild_icon.url if guild_icon else ""
        else:
            member_avatar = message.author.avatar_url  # type: ignore
            guild_icon = message.guild.icon_url  # type: ignore
            bot_avatar = message.guild.me.avatar_url  # type: ignore

        return SubstituteArgs(
            bot_id=message.guild.me.id,
            bot_name=message.guild.me.name,
            bot_avatar=bot_avatar,
            guild_id=message.guild.id,
            guild_icon=guild_icon,
            guild_name=message.guild.name,
            member_id=message.author.id,
            member_name=message.author.display_name,
            member_avatar=member_avatar,
        )

    async def create_message(self, message: discord.Message) -> Message:
        log.debug(
            "Attempting to create a new message for author(id=%s) in Guild(%s)",
            message.author.id,
            message.guild.id,
        )
        if message.is_system():
            raise InvalidMessage(
                "Message is a system one, we don't check against those."
            )

        content = ""
        if message.stickers:
            # 'sticker' urls should be unique..
            all_stickers = "|".join(s.url for s in message.stickers)
            content += all_stickers

        elif not bool(message.content and message.content.strip()):
            if not message.embeds and not message.attachments:
                # System message? Like on join trip these
                raise InvalidMessage("We don't check against system messages")

            if not message.embeds:
                # We don't check against attachments
                raise InvalidMessage("We don't check against attachments")

            for embed in message.embeds:
                if not isinstance(embed, discord.Embed):
                    raise InvalidMessage("embed was not of instance discord.Embed")

                if embed.type.lower() != "rich":
                    raise InvalidMessage("Only rich embeds are supported")

                content += await self.embed_to_string(embed)
        else:
            content += message.clean_content

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
            channel_id=message.channel.id,
            guild_id=message.guild.id,
            author_id=message.author.id,
            content=content,
        )

    async def send_guild_log(
        self,
        guild,
        message: Union[str, discord.Embed],
        delete_after_time,
        original_channel: Union[discord.abc.GuildChannel, discord.abc.PrivateChannel],
        file=None,
    ) -> None:  # pragma: no cover
        try:
            if not guild.log_channel_id:
                log.debug(
                    "Guild(id=%s) has no log channel set, not sending message.",
                    guild.id,
                )
                return

            channel = guild.log_channel_id

            channel = self.bot.get_channel(channel)
            if not channel:
                channel = await self.bot.fetch_channel(channel)

            if isinstance(message, str):
                await channel.send(message, delete_after=delete_after_time, file=file)
            else:
                await channel.send(
                    embed=message, file=file, delete_after=delete_after_time
                )

            log.debug("Sent message to log channel in Guild(id=%s)", guild.id)
        except discord.HTTPException:
            log.error(
                "Failed to send log message in Guild(id=%s). HTTPException", guild.id
            )

    async def punish_member(
        self,
        original_message: discord.Message,
        member: Member,
        internal_guild: Guild,
        user_message,
        guild_message,
        is_kick: bool,
        user_delete_after: int = None,
        channel_delete_after: int = None,
    ) -> bool:  # pragma: no cover
        guild = original_message.guild
        author = original_message.author

        # Check we have perms to punish
        perms = guild.me.guild_permissions
        if not perms.kick_members and is_kick:
            member.internal_is_in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need kick perms to punish someone in {guild.name}"
            )

        elif not perms.ban_members and not is_kick:
            member.internal_is_in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need ban perms to punish someone in {guild.name}"
            )

        # We also check they don't own the guild, since ya know...
        elif guild.owner_id == member.id:
            member.internal_is_in_guild = True
            member.kick_count -= 1

            await self.send_guild_log(
                guild=internal_guild,
                message=f"I am failing to punish {original_message.author.display_name} because they own this guild.",
                delete_after_time=channel_delete_after,
                original_channel=original_message.channel,
            )
            raise MissingGuildPermissions(
                f"I cannot punish {author.display_name}({author.id}) "
                f"because they own this guild. ({guild.name})"
            )

        # Ensure we can actually punish the user, for this
        # we just check our top role is higher then them
        elif guild.me.top_role.position < author.top_role.position:
            log.warning(
                "I might not be able to punish %s(%s) in Guild: %s(%s) "
                "because they are higher then me, which means I could lack the ability to kick/ban them.",
                author.display_name,
                member.id,
                guild.name,
                guild.id,
            )

        sent_message: Optional[discord.Message] = None
        try:
            if isinstance(user_message, discord.Embed):
                sent_message = await author.send(
                    embed=user_message, delete_after=user_delete_after
                )
            else:
                sent_message = await author.send(
                    user_message, delete_after=user_delete_after
                )

        except discord.HTTPException:
            await self.send_guild_log(
                guild=internal_guild,
                message=f"Sending a message to {author.mention} about their {'kick' if is_kick else 'ban'} failed.",
                delete_after_time=channel_delete_after,
                original_channel=original_message.channel,
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
                    member, reason="Automated punishment from DPY Anti-Spam."
                )
                log.info("Kicked Member(id=%s)", member.id)
            else:
                await guild.ban(
                    member, reason="Automated punishment from DPY Anti-Spam."
                )
                log.info("Banned Member(id=%s)", member.id)

        except discord.Forbidden as e:
            # In theory we send the failed punishment method
            # here, although we check first so I think its fine
            # to remove it from this part
            raise e from None

        except discord.HTTPException:
            _success = False
            member.internal_is_in_guild = True
            member.kick_count -= 1
            await self.send_guild_log(
                guild=internal_guild,
                message=f"An error occurred trying to {'kick' if is_kick else 'ban'}: <@{member.id}>",
                delete_after_time=channel_delete_after,
                original_channel=original_message.channel,
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
                    internal_guild,
                    user_failed_message,
                    channel_delete_after,
                    original_message.channel,
                )
                await sent_message.delete()

        else:
            await self.send_guild_log(
                guild=internal_guild,
                message=guild_message,
                delete_after_time=channel_delete_after,
                original_channel=original_message.channel,
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
        bot = self.bot
        channels = {}
        for message in member.messages:
            if message.is_duplicate:
                # cache channel for further fetches
                if message.channel_id not in channels:
                    channel = bot.get_channel(message.channel_id)
                    if not channel:
                        channel = await bot.fetch_channel(message.channel_id)

                    channels[message.channel_id] = channel
                else:
                    channel = channels[message.channel_id]

                try:
                    actual_message = await channel.fetch_message(message.id)
                    await self.delete_message(actual_message)
                except discord.NotFound:
                    continue

    async def delete_message(
        self, message: discord.Message
    ) -> None:  # pragma: no cover
        try:
            await message.delete()
            log.debug("Deleted message %s", message.id)
        except discord.HTTPException:
            # Failed to delete message
            log.warning(
                "Failed to delete message %s in Guild(id=%s). HTTPException",
                message.id,
                message.guild.id,
            )

    async def send_message_to_(
        self,
        target: discord.abc.Messageable,
        message: Union[str, discord.Embed],
        mention: str,
        delete_after_time: Optional[int] = None,
    ) -> None:  # pragma: no cover
        if isinstance(message, discord.Embed):
            content = None
            if self.handler.options.mention_on_embed:
                content = mention
            await target.send(
                content,
                embed=message,
                delete_after=delete_after_time,
            )
        else:
            await target.send(
                message,
                delete_after=delete_after_time,
            )

    async def timeout_member(
        self, member, original_message, until: datetime.timedelta
    ) -> None:
        raise UnsupportedAction(
            "Timeouts are not supported for discord.py, if you "
            "are using a fork please specify it explicitly."
        )

    async def is_member_currently_timed_out(self, member) -> bool:
        raise UnsupportedAction(
            "Timeouts are not supported for discord.py, if you "
            "are using a fork please specify it explicitly."
        )

    def is_dm(self, message) -> bool:
        return not bool(message.guild)
