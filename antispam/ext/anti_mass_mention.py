import datetime
import typing
from dataclasses import dataclass, asdict

import discord

from antispam.exceptions import UserNotFound
from antispam.base_extension import BaseExtension
from antispam.ext.user_tracking import UserTracking


@dataclass
class MassMentionPunishment:
    """
    This dataclass is what is dispatched to
    `on_mass_mention_punishment`

    Parameters
    ----------
    user_id : int
        The associated users id
    guild_id : int
        The associated guilds id
    is_overall_punishment : bool
        If this is ``True``, it means the user
        has exceeded ``total_mentions_before_punishment``.
        Otherwise they have exceeded ``min_mentions_per_message``
    """

    user_id: int
    guild_id: int
    is_overall_punishment: bool


@dataclass
class Tracking:
    mentions: int
    timestamp: datetime.datetime


class AntiMassMention(BaseExtension):
    """A simple class used to track mentions"""

    def __init__(
        self,
        bot,
        *,
        total_mentions_before_punishment: int = 10,
        time_period: int = 15000,
        min_mentions_per_message: int = 5
    ):
        """

        Parameters
        ----------
        bot : commands.Bot or commands.AutoShardedBot or discord.Client or discord.AutoShardedClient
            Our bot instance
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
        self.bot = bot
        self.data = UserTracking()

        if min_mentions_per_message > total_mentions_before_punishment:
            raise ValueError(
                "Expected `min_mentions_per_message` to be less then or equal to `total_mentions_before_punishment`"
            )

        if time_period < 1:
            raise ValueError("Expected `time_period` to be positive")

        self.min_mentions_per_message = min_mentions_per_message
        self.total_mentions_before_punishment = total_mentions_before_punishment
        self.time_period = time_period

    async def propagate(
        self, message: discord.Message, data: typing.Optional[dict] = None
    ) -> dict:
        """
        Manages and stores any mass mentions per users
        Parameters
        ----------
        message : discord.Message
            The message to interact with
        data : None
            Not expected/wanted

        Returns
        -------
        dict
            A dictionary explaining what
            actions have been taken
        """
        user_id = message.author.id
        guild_id = message.guild.id

        try:
            user = self.data.get_user(guild_id, user_id)
        except UserNotFound:
            user = {"total_mentions": []}
            """
            {
                "total_mentions": [
                    {
                        int amount : Datetime timestamp
                    }
                ]
            }
            """

        mentions = set(message.mentions)
        user["total_mentions"].append(
            Tracking(mentions=len(mentions), timestamp=message.created_at)
        )
        self.data.set_user(guild_id, user_id, user)
        self._clean_mention_timestamps(
            guild_id=guild_id,
            user_id=user_id,
            current_time=datetime.datetime.now(datetime.timezone.utc),
        )

        if len(mentions) >= self.min_mentions_per_message:
            # They mention too many people in this message so punish
            payload = MassMentionPunishment(
                user_id=user_id,
                guild_id=guild_id,
                is_overall_punishment=False,
            )
            self.bot.dispatch(
                "mass_mention_punishment",
                payload,
            )
            return asdict(payload)

        user = self.data.get_user(guild_id=guild_id, user_id=user_id)
        if (
            sum(item.timestamp for item in user["total_mentions"])
            >= self.total_mentions_before_punishment
        ):
            # They have more mentions are cleaning then allowed,
            # So time to punish them
            payload = MassMentionPunishment(
                user_id=user_id,
                guild_id=guild_id,
                is_overall_punishment=True,
            )
            self.bot.dispatch(
                "mass_mention_punishment",
                payload,
            )
            return asdict(payload)

        return {"action": "No action taken"}

    def _clean_mention_timestamps(
        self, guild_id: int, user_id: int, current_time: datetime.datetime
    ):
        """
        Cleans the internal cache for a user to only keep current mentions
        Parameters
        ----------
        guild_id : int
            The guild the users in
        user_id : int
            The user to clean

        Notes
        -----
        Expects the user to exist in ``self.data``. This
        does no form of validation for existence

        """

        def _is_still_valid(timestamp):
            difference = current_time - timestamp
            offset = datetime.timedelta(milliseconds=self.time_period)

            if difference >= offset:
                return False
            return True

        user = self.data.get_user(guild_id=guild_id, user_id=user_id)
        valid_items = []
        for item in user["total_mentions"]:
            if _is_still_valid(item.timestamp):
                valid_items.append(item)

        user["total_mentions"] = valid_items
        self.data.set_user(guild_id=guild_id, user_id=user_id)
