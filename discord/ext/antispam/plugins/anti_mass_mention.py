import logging
import datetime

import attr
from attr import asdict

import discord  # noqa

from discord.ext.antispam.exceptions import MemberNotFound  # noqa
from discord.ext.antispam.base_plugin import BasePlugin  # noqa
from discord.ext.antispam.plugin_cache import PluginCache  # noqa
from discord.ext.antispam import AntiSpamHandler, GuildNotFound  # noqa

from discord.ext.antispam.util import get_aware_time

log = logging.getLogger(__name__)


@attr.s
class MassMentionPunishment:
    # noinspection PyUnresolvedReferences
    """
    This dataclass is what is dispatched to
    `on_mass_mention_punishment`

    Parameters
    ----------
    member_id : int
        The associated users id
    guild_id : int
        The associated guilds id
    is_overall_punishment : bool
        If this is ``True``, it means the user
        has exceeded ``total_mentions_before_punishment``.
        Otherwise they have exceeded ``min_mentions_per_message``
    """

    member_id: int = attr.ib()
    guild_id: int = attr.ib()
    is_overall_punishment: bool = attr.ib()


@attr.s
class Tracking:
    mentions: int = attr.ib()
    timestamp: datetime.datetime = attr.ib()


class AntiMassMention(PluginCache):
    """A simple class used to track mentions"""

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
        bot : commands.Bot or commands.AutoShardedBot or discord.Client or discord.AutoShardedClient
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
        self.data = PluginCache(handler, caller=self)

        self.min_mentions_per_message = min_mentions_per_message
        self.total_mentions_before_punishment = total_mentions_before_punishment
        self.time_period = time_period

        log.debug("Initialized AntiMassMention")

    async def propagate(self, message: discord.Message) -> dict:
        """
        Manages and stores any mass mentions per users
        Parameters
        ----------
        message : discord.Message
            The message to interact with

        Returns
        -------
        dict
            A dictionary explaining what
            actions have been taken
        """
        member_id = message.author.id
        guild_id = message.guild.id

        log.debug(f"Propagating message for {member_id}, guild:{guild_id}")

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

        mentions = set(message.mentions)
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
            log.info("Dispatching punishment event, is_overall_punishment=False")
            payload = MassMentionPunishment(
                member_id=member_id,
                guild_id=guild_id,
                is_overall_punishment=False,
            )
            self.bot.dispatch(
                "mass_mention_punishment",
                payload,
            )
            return asdict(payload)

        member = await self.data.get_member_data(guild_id=guild_id, member_id=member_id)
        if (
            sum(item.mentions for item in member["total_mentions"])
            >= self.total_mentions_before_punishment
        ):
            # They have more mentions are cleaning then allowed,
            # So time to punish them
            log.info("Dispatching punishment event, is_overall_punishment=True")
            payload = MassMentionPunishment(
                member_id=member_id,
                guild_id=guild_id,
                is_overall_punishment=True,
            )
            self.bot.dispatch(
                "mass_mention_punishment",
                payload,
            )
            return asdict(payload)

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
        log.debug(f"Cleaning timestamps for {member_id}, guild: {guild_id}")

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
            # TODO This might break in dpy 2.0
            make_aware = item.timestamp.replace(tzinfo=datetime.timezone.utc)
            if await _is_still_valid(make_aware):
                valid_items.append(item)

        member["total_mentions"] = valid_items
        await self.data.set_member_data(member_id, guild_id, addon_data=member)
