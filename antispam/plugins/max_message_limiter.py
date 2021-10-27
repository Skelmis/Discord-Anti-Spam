import asyncio
import logging
from typing import Optional, Any

from antispam import (
    BasePlugin,
    CorePayload,
    AntiSpamHandler,
    MemberNotFound,
    GuildNotFound,
)
from antispam.abc import Cache
from antispam.dataclasses import Member

try:
    import nextcord as discord
except ModuleNotFoundError:
    try:
        import discord
    except ModuleNotFoundError:
        raise RuntimeError(
            "This plugin only supports discord.py and its forks."
        ) from None

log = logging.getLogger(__name__)


class MaxMessageLimiter(BasePlugin):
    """
    This plugin implements a hard cap for the amount
    of messages a member can send within the handlers timeframe
    before losing send message perms.

    The

    Notes
    -----
    This is per channel and only works with the initial
    message_interval, no updates or guild specifics. If this
    is something you want let me know on discord and I'll make it.
    """

    def __init__(self, handler: AntiSpamHandler, hard_cap: int = 25):
        """
        Parameters
        ----------
        handler : AntiSpamHandler
            The handler to extract cache from
        hard_cap : int, Optional
            The hard cap for the amount of messages you
            can send within ``message_interval``
        """
        super().__init__(is_pre_invoke=False)
        self.hard_cap: int = hard_cap
        self.primary_cache: Cache = handler.cache
        log.info("Plugin ready for usage")

    async def propagate(self, message, data: Optional[CorePayload] = None) -> Any:
        try:
            member: Member = await self.primary_cache.get_member(
                message.author.id, message.guild.id
            )
        except (MemberNotFound, GuildNotFound):
            # If they don't exist they havent exceeded limits
            return None

        messages_in_channel = [
            m for m in member.messages if m.channel_id == message.channel.id
        ]

        if len(messages_in_channel) < self.hard_cap:
            return "Under hard cap"

        await self.do_punishment(member, message)

    async def do_punishment(self, member: Member, message) -> None:
        """
        This method gets called and handles punishments,
        override it to change punishments.

        Parameters
        ----------
        member : Member
            The member to punish
        message
            A message to get info from
        """
        channel: discord.TextChannel = message.channel
        overwrites = channel.overwrites

        # Remove perms to speak
        overwrites[message.author] = discord.PermissionOverwrite(send_messages=False)
        await channel.edit(overwrites=overwrites)
        log.info(
            "Removed Member(id=%s)'s perms to speak in Channel(%s) for Guild(id=%s)",
            member.id,
            channel.id,
            message.guild.id,
        )
        await asyncio.sleep(60)
        # Give back said perms
        overwrites[message.author] = discord.PermissionOverwrite(send_messages=None)
        await channel.edit(overwrites=overwrites)
        log.info(
            "Gave back Member(id=%s)'s perms to speak in Channel(%s) for Guild(id=%s)",
            member.id,
            channel.id,
            message.guild.id,
        )
