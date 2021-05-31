import typing
from dataclasses import dataclass

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
        try:
            user = self.data.get_user(message.guild.id, message.author.id)
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
        if len(mentions) >= self.min_mentions_per_message:
            self.bot.dispatch(
                "mass_mention_punishment",
            )

        user["total_mentions"].append({len(mentions): message.created_at})
        self.data.set_user(message.guild.id, message.author.id, user)

    def _clean_mention_timestamps(self, guild_id: int, user_id: int):
        """
        Cleans the internal cache for a user to only keep current mentions
        Parameters
        ----------
        guild_id
        user_id

        Returns
        -------

        """
