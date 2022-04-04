import asyncio
import datetime
import logging
from typing import Any, Optional, TYPE_CHECKING

from antispam import (
    AntiSpamHandler,
    BasePlugin,
    CorePayload,
    GuildNotFound,
    MemberNotFound,
)
from antispam.abc import Cache
from antispam.dataclasses import Member
from antispam.util import get_aware_time

if TYPE_CHECKING:
    from antispam.abc import Lib

log = logging.getLogger(__name__)


class MaxMessageLimiter(BasePlugin):
    """
    This plugin implements a hard cap for the amount
    of messages a member can send within the handlers timeframe
    before losing send message perms.

    Notes
    -----
    This only works with the initial
    message_interval, no updates or guild specifics. If this
    is something you want let me know on discord and I might make it.

    This is also guild wide.
    """

    def __init__(
        self,
        handler: AntiSpamHandler,
        hard_cap: int = 50,
        message_interval: Optional[int] = None,
    ):
        """
        Parameters
        ----------
        handler : AntiSpamHandler
            The handler to extract cache from
        hard_cap : int, Optional
            The hard cap for the amount of messages you
            can send within ``message_interval``

            Defaults to ``50``

        message_interval: int, Optional
            The period of time in milliseconds which
            messages should be treated as valid.

            Defaults to your AntiSpamHandler options message_interval
        """
        super().__init__(is_pre_invoke=False)
        self.hard_cap: int = hard_cap
        self.primary_cache: Cache = handler.cache
        self.lib_handler: "Lib" = handler.lib_handler
        self.message_interval: int = (
            message_interval or handler.options.message_interval
        )
        log.info("Plugin ready for usage")

    async def propagate(self, message, data: Optional[CorePayload] = None) -> Any:
        try:
            member: Member = await self.primary_cache.get_member(
                message.author.id, message.guild.id
            )
        except (MemberNotFound, GuildNotFound):
            # If they don't exist they haven't exceeded limits
            return None

        messages_in_channel = [
            m
            for m in member.messages
            if m.channel_id == message.channel.id
            and (
                m.creation_time + datetime.timedelta(milliseconds=self.message_interval)
            )
            >= get_aware_time()
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
        author = await self.lib_handler.get_member_from_message(message)
        await self.lib_handler.timeout_member(
            author, message, datetime.timedelta(minutes=5)
        )

        log.info(
            "Timed out Member(id=%s)'s in Guild(id=%s)",
            author.id,
            message.guild.id,
        )
