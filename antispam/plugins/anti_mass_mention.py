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
from typing import Union

import attr

from antispam import AntiSpamHandler, GuildNotFound, PluginCache
from antispam.base_plugin import BasePlugin
from antispam.exceptions import MemberNotFound
from antispam.util import get_aware_time

log = logging.getLogger(__name__)


@attr.s
class MassMentionPunishment:
    # noinspection PyUnresolvedReferences
    """
    This dataclass is what is dispatched
    when someone should be punished for mention spam.

    Parameters
    ----------
    member_id : int
        The associated members id
    channel_id : int
        The associated channels id
    guild_id : int
        The associated guilds id
    is_overall_punishment : bool
        If this is ``True``, it means the user
        has exceeded ``total_mentions_before_punishment``.
        Otherwise they have exceeded ``min_mentions_per_message``

    Notes
    -----
    You shouldn't be making instances of this.
    """

    member_id: int = attr.ib()
    guild_id: int = attr.ib()
    channel_id: int = attr.ib()
    is_overall_punishment: bool = attr.ib()


@attr.s
class Tracking:
    mentions: int = attr.ib()
    timestamp: datetime.datetime = attr.ib()


class AntiMassMention(BasePlugin):
    """
    In order to check if you should punish someone,
    see the below code.

    .. code-block:: python
        :linenos:

        data = await AntiSpamHandler.propagate(message)
        return_item: Union[dict, MassMentionPunishment] = data.after_invoke_plugins["AntiMassMention"]

        if isinstance(return_item, MassMentionPunishment):
            # Punish for mention spam
    """

    def __init__(
        self,
        bot,
        handler: AntiSpamHandler,
        *,
        total_mentions_before_punishment: int = 10,
        time_period: int = 15000,
        min_mentions_per_message: int = 5,
    ):
        """

        Parameters
        ----------
        bot
            Our bot instance
        handler : AntiSpamHandler
            Our AntiSpamHandler instance
        total_mentions_before_punishment : int
            How many mentions within the time period
            before we punish the user
            *Inclusive*
        time_period : int
            The time period valid for mentions
            *Is in milliseconds*
        min_mentions_per_message : int
            The minimum amount of mentions in a message
            before a punishment is issued
            *Inclusive*
        """
        super().__init__()
        if min_mentions_per_message > total_mentions_before_punishment:
            raise ValueError(
                "Expected `min_mentions_per_message` to be less then or equal to `total_mentions_before_punishment`"
            )

        if time_period < 1:
            raise ValueError("Expected `time_period` to be positive")

        self.bot = bot
        self.handler = handler
        self.data = PluginCache(handler, caller=self)

        self.min_mentions_per_message = min_mentions_per_message
        self.total_mentions_before_punishment = total_mentions_before_punishment
        self.time_period = time_period

        log.info("Plugin ready for usage")

    async def propagate(self, message) -> Union[dict, MassMentionPunishment]:
        """
        Manages and stores any mass mentions per users

        Parameters
        ----------
        message
            The message to interact with

        Returns
        -------
        dict
            A dictionary explaining what
            actions have been taken
        MassMentionPunishment
            Data surrounding the punishment
            you should be doing.
        """
        member_id = message.author.id
        guild_id = await self.handler.lib_handler.get_guild_id(message)

        log.info(
            "Propagating message for Member(id=%s) in Guild(id=%s)", member_id, guild_id
        )

        try:
            member = await self.data.get_member_data(member_id, guild_id)
        except (MemberNotFound, GuildNotFound):
            member = {"total_mentions": []}
            """
            {
                "total_mentions": [
                    Tracking(),
                ]
            }
            """

        mentions = set(await self.handler.lib_handler.get_message_mentions(message))
        member["total_mentions"].append(
            Tracking(mentions=len(mentions), timestamp=message.created_at)
        )
        await self.data.set_member_data(member_id, guild_id, member)
        await self._clean_mention_timestamps(
            guild_id=guild_id,
            member_id=member_id,
            current_time=get_aware_time(),
        )

        if len(mentions) >= self.min_mentions_per_message:
            # They mention too many people in this message so punish
            log.info("Dispatching punishment, is_overall_punishment=False")
            payload = MassMentionPunishment(
                member_id=member_id,
                guild_id=guild_id,
                channel_id=await self.handler.lib_handler.get_channel_id(message),
                is_overall_punishment=False,
            )
            return payload

        member = await self.data.get_member_data(guild_id=guild_id, member_id=member_id)
        if (
            sum(item.mentions for item in member["total_mentions"])
            >= self.total_mentions_before_punishment
        ):
            # They have more mentions are cleaning then allowed,
            # So time to punish them
            log.info("Dispatching punishment, is_overall_punishment=True")
            payload = MassMentionPunishment(
                member_id=member_id,
                guild_id=guild_id,
                channel_id=await self.handler.lib_handler.get_channel_id(message),
                is_overall_punishment=True,
            )
            return payload

        return {"action": "No action taken"}

    async def _clean_mention_timestamps(
        self, guild_id: int, member_id: int, current_time: datetime.datetime
    ):
        """
        Cleans the internal cache for a member to only keep current mentions
        Parameters
        ----------
        guild_id : int
            The guild the users in
        member_id : int
            The member to clean

        Notes
        -----
        If the member does not exist in ``self.data``,
        they are ignored and this method returns

        """
        log.debug(
            "Cleaning timestamps for Member(id=%s) in Guild(id=%s)", member_id, guild_id
        )

        async def _is_still_valid(timestamp):
            difference = current_time - timestamp
            offset = datetime.timedelta(milliseconds=self.time_period)

            if difference >= offset:
                return False
            return True

        try:
            member = await self.data.get_member_data(
                guild_id=guild_id, member_id=member_id
            )
        except (GuildNotFound, MemberNotFound):
            return

        valid_items = []
        for item in member["total_mentions"]:
            make_aware = item.timestamp.replace(tzinfo=datetime.timezone.utc)
            if await _is_still_valid(make_aware):
                valid_items.append(item)

        member["total_mentions"] = valid_items
        await self.data.set_member_data(member_id, guild_id, addon_data=member)
