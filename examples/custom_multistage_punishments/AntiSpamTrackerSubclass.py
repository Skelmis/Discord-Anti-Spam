"""Our subclass of AntiSpamTracker"""
import asyncio
import datetime
from copy import deepcopy

import discord

from discord.ext.antispam import MemberNotFound
from discord.ext.antispam import AntiSpamTracker


# noinspection DuplicatedCode
class MyCustomTracker(AntiSpamTracker):
    def update_cache(self, message: discord.Message, data: dict) -> None:
        """Override this so we can add a custom field to the stored user"""

        user_id = message.author.id
        guild_id = message.guild.id
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        if guild_id not in self.user_tracking:
            self.user_tracking[guild_id] = {}

        if user_id not in self.user_tracking[guild_id]:
            self.user_tracking[guild_id][user_id] = {}

        if "has_been_muted" not in self.user_tracking[guild_id][user_id]:
            self.user_tracking[guild_id][user_id]["has_been_muted"] = False

        if "timestamps" not in self.user_tracking[guild_id][user_id]:
            self.user_tracking[guild_id][user_id]["timestamps"] = []

        self.user_tracking[guild_id][user_id]["timestamps"].append(timestamp)

    def get_user_has_been_muted(self, message: discord.Message) -> bool:
        """
        Returns if the user for the associated message
        has been muted yet or not.


        Parameters
        ----------
        message : discord.Message
            The message from which to extract user

        Returns
        -------
        bool
            True if the user has been muted
            before else False

        Raises
        ------
        UserNotFound
            The User for the ``message`` could not be found

        """
        user_id = message.author.id
        guild_id = message.guild.id

        if guild_id not in self.user_tracking:
            raise MemberNotFound

        if user_id not in self.user_tracking[guild_id]:
            raise MemberNotFound

        return self.user_tracking[guild_id][user_id]["has_been_muted"]

    async def do_punishment(self, message: discord.Message, *args, **kwargs) -> None:
        """
        We do the punishment by checking ``self.is_spamming``.
        The first punishment is a mute, followed
        by the next punishment being removal from the guild

        Parameters
        ----------
        message : discord.Message
            The message to get the attached user from

        """
        if message.author.id == self.anti_spam_handler.bot.user.id:
            return

        user = message.author
        guild = message.guild
        channel = message.channel
        user_id = message.author.id
        guild_id = message.guild.id

        has_been_muted = self.get_user_has_been_muted(message=message)

        if has_been_muted:
            # User has been muted before, time to kick em
            await channel.send(f"Hey {user.mention}! I am kicking you for spam.")
            await asyncio.sleep(2.5)
            await guild.kick(user, reason="Kicked for spam.")
            self.remove_punishments(
                message
            )  # cleanup on the assumption they won't 'just come back'

        elif self.is_spamming(message=message):
            self.user_tracking[guild_id][user_id]["has_been_muted"] = True
            await channel.send(f"Hey {user.mention}! I am temp muting you for spam.")

            guild = self.anti_spam_handler.bot.get_guild(guild_id)
            mute_role = guild.get_role(
                836206352966877225
            )  # <-- Add your role id in there
            await user.add_roles(mute_role, reason="Temp-muted for spam.")

            await asyncio.sleep(30)  # Mute for 5 minutes
            await user.remove_roles(mute_role, reason="Automatic un-mute.")
            await channel.send(
                f"Hey {user.mention}, I have un-muted you. Don't do it again."
            )

    def clean_cache(self) -> None:
        """Override this so if the has_been_muted field exists we don't remove them"""
        for guild_id, guild in deepcopy(self.user_tracking).items():
            for user_id, user in deepcopy(guild).items():
                self.remove_outdated_timestamps(guild_id=guild_id, user_id=user_id)

                if len(self.user_tracking[guild_id][user_id]) == 0 and not user.get(
                    "has_been_muted", True
                ):
                    self.user_tracking[guild_id].pop(user_id)

            if not bool(self.user_tracking[guild_id]):
                self.user_tracking.pop(guild_id)

    def get_user_count(self, message: discord.Message) -> int:
        if not isinstance(message, discord.Message):
            raise TypeError("Expected message of type: discord.Message")

        if not message.guild:
            raise MemberNotFound("Can't find user's from dm's")

        user_id = message.author.id
        guild_id = message.guild.id

        if guild_id not in self.user_tracking:
            raise MemberNotFound

        if user_id not in self.user_tracking[guild_id]:
            raise MemberNotFound

        if "timestamps" not in self.user_tracking[guild_id][user_id]:
            raise MemberNotFound

        self.remove_outdated_timestamps(guild_id=guild_id, user_id=user_id)

        return len(self.user_tracking[guild_id][user_id]["timestamps"])

    def remove_outdated_timestamps(self, guild_id, user_id):
        current_time = datetime.datetime.now(datetime.timezone.utc)

        def _is_still_valid(timestamp):
            difference = current_time - timestamp
            offset = datetime.timedelta(
                milliseconds=self._get_guild_valid_interval(guild_id=guild_id)
            )

            if difference >= offset:
                return False
            return True

        current_timestamps = []

        for timestamp in self.user_tracking[guild_id][user_id]["timestamps"]:
            if _is_still_valid(timestamp):
                current_timestamps.append(timestamp)

        self.user_tracking[guild_id][user_id]["timestamps"] = deepcopy(
            current_timestamps
        )
