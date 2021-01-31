"""Our subclass of AntiSpamTracker - I haven't tested this. That is up to you to do. Use this as a 'blueprint'"""
import asyncio
from copy import deepcopy

import discord

from AntiSpam import AntiSpamTracker, UserNotFound


class MyCustomTracker(AntiSpamTracker):
    def update_cache(self, message: discord.Message, data: dict) -> None:
        """Override this so we can add a custom field to the stored user"""
        super().update_cache(message=message, data=data)

        user_id = message.author.id
        guild_id = message.guild.id

        if "has_been_muted" not in self.user_tracking[guild_id][user_id]:
            self.user_tracking[guild_id][user_id]["has_been_muted"] = False

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
            raise UserNotFound

        if user_id not in self.user_tracking[guild_id]:
            raise UserNotFound

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

            mute_role = guild_id.get_role(12345)  # <-- Add your role id in there
            await user.add_roles(mute_role, reason="Temp-muted for spam.")

            await asyncio.sleep(300)  # Mute for 5 minutes
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
