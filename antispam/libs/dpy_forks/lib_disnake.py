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
import logging
from unittest.mock import AsyncMock

import disnake

from antispam import MissingGuildPermissions, PropagateFailure
from antispam.dataclasses.propagate_data import PropagateData
from antispam.deprecation import mark_deprecated
from antispam.libs.dpy_forks import BaseFork

log = logging.getLogger(__name__)

# noinspection DuplicatedCode
class Disnake(BaseFork):
    async def timeout_member(
        self, member: disnake.Member, original_message, until: datetime.timedelta
    ) -> None:
        guild = original_message.guild
        perms = guild.me.guild_permissions
        if not perms.moderate_members:
            raise MissingGuildPermissions(
                "moderate_members is required to timeout members.\n"
                f"Tried timing out Member(id={member.id}) in Guild(id={member.guild.id})"
            )

        await member.timeout(
            duration=until, reason="Automated timeout from Discord-Anti-Spam"
        )

    async def check_message_can_be_propagated(
        self, message: disnake.Message
    ) -> PropagateData:
        # We need to do this with the disnake namespace
        if not isinstance(message, (disnake.Message, AsyncMock)):
            raise PropagateFailure(
                data={"status": "Expected message of type discord.Message"}
            )

        # Ensure we only moderate actual guild messages
        if not message.guild:
            log.debug(
                "Message(id=%s) from Member(id=%s) was not in a guild",
                message.id,
                message.author.id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from dm's"})

        # The bot is immune to spam
        if message.author.id == self.bot.user.id:
            log.debug("Message(id=%s) was from myself", message.id)
            raise PropagateFailure(
                data={"status": "Ignoring messages from myself (the bot)"}
            )

        if isinstance(message.author, disnake.User):  # pragma: no cover
            log.warning(f"Given Message(id=%s) with an author of type User", message.id)

        # Return if ignored bot
        if self.handler.options.ignore_bots and message.author.bot:
            log.debug(
                "I ignore bots, and this is a bot message with author(id=%s)",
                message.author.id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from bots"})

        # Return if ignored guild
        if message.guild.id in self.handler.options.ignored_guilds:
            log.debug("Ignored Guild(id=%s)", message.guild.id)
            raise PropagateFailure(
                data={"status": f"Ignoring this guild: {message.guild.id}"}
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
        if message.channel.id in self.handler.options.ignored_channels:
            log.debug("channel(id=%s) is ignored", message.channel.id)
            raise PropagateFailure(
                data={"status": f"Ignoring this channel: {message.channel.id}"}
            )

        # Return if member has an ignored role
        try:
            user_roles = [role.id for role in message.author.roles]
            for item in user_roles:
                if item in self.handler.options.ignored_roles:
                    log.debug(
                        "Ignoring Member(id=%s) as they have an ignored Role(id/name=%S)",
                        message.author.id,
                        item,
                    )
                    raise PropagateFailure(
                        data={"status": f"Ignoring this role: {item}"}
                    )
        except AttributeError:  # pragma: no cover
            log.warning(
                "Could not compute ignored_roles for %s(%s)",
                message.author.name,
                message.author.id,
            )

        perms = message.guild.me.guild_permissions
        has_perms = perms.kick_members and perms.ban_members

        return PropagateData(
            guild_id=message.guild.id,
            member_name=message.author.name,
            member_id=message.author.id,
            has_perms_to_make_guild=has_perms,
        )

    async def is_member_currently_timed_out(self, member: disnake.Member) -> bool:
        return bool(member.current_timeout)
