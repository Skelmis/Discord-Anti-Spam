"""Our subclass of AntiSpamTracker"""
import asyncio
import datetime
import typing
from copy import deepcopy

import discord

from antispam import MemberNotFound, GuildNotFound
from antispam.dataclasses import Guild, Member
from antispam.plugins import AntiSpamTracker


# noinspection DuplicatedCode
class MyCustomTracker(AntiSpamTracker):
    def update_cache(self, message: discord.Message, data: dict) -> None:
        """Override this so we can add a custom field to the stored user"""

        member_id = message.author.id
        guild_id = message.guild.id
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        try:
            member_data = await self.member_tracking.get_member_data(
                member_id, guild_id
            )
        except (MemberNotFound, GuildNotFound):
            member_data = {"has_been_muted": False, "timestamps": []}

        member_data["timestamps"].append(timestamp)
        await self.member_tracking.set_member_data(member_id, guild_id, member_data)

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
        member_id = message.author.id
        guild_id = message.guild.id

        try:
            member_data = await self.member_tracking.get_member_data(
                member_id, guild_id
            )
        except GuildNotFound as e:
            raise MemberNotFound from e

        return member_data["has_been_muted"]

    async def do_punishment(self, message: discord.Message, *args, **kwargs) -> None:
        """
        We do the punishment by checking ``self.is_spamming``.
        The first punishment is a mute, followed
        by the next punishment being removal from the guild

        Parameters
        ----------
        message : discord.Message
            The message to get the attached user from

        Notes
        -----
        This assumes the member exists, it does
        no error handling for if they don't.

        """
        if message.author.id == self.anti_spam_handler.bot.user.id:
            return

        member = message.author
        guild = message.guild
        channel = message.channel
        member_id = message.author.id
        guild_id = message.guild.id

        has_been_muted = self.get_user_has_been_muted(message=message)
        member_data = await self.member_tracking.get_member_data(member_id, guild_id)

        if has_been_muted:
            # User has been muted before, time to kick em
            await channel.send(f"Hey {member.mention}! I am kicking you for spam.")
            await asyncio.sleep(2.5)
            await guild.kick(member, reason="Kicked for spam.")
            # cleanup on the assumption they won't 'just come back'
            await self.remove_punishments(message)

        elif self.is_spamming(message=message):
            member_data["has_been_muted"] = True
            await self.member_tracking.set_member_data(member_id, guild_id, member_data)
            await channel.send(f"Hey {member.mention}! I am temp muting you for spam.")

            guild = self.anti_spam_handler.bot.get_guild(guild_id)
            mute_role = guild.get_role(
                836206352966877225
            )  # <-- Add your role id in there
            await member.add_roles(mute_role, reason="Temp-muted for spam.")

            await asyncio.sleep(30)  # Mute for 5 minutes
            await member.remove_roles(mute_role, reason="Automatic un-mute.")
            await channel.send(
                f"Hey {member.mention}, I have un-muted you. Don't do it again."
            )

    def clean_cache(self) -> None:
        """Override this so if the has_been_muted field exists we don't remove them"""
        cache: typing.AsyncIterable[
            Guild
        ] = await self.anti_spam_handler.cache.get_all_guilds()

        async for guild in cache:
            for member in guild.members.values():
                self.remove_outdated_timestamps(
                    member.addons[super().__class__.__name__],
                    member_id=member.id,
                    guild_id=guild.id,
                )

                member_data = await self.member_tracking.get_member_data(
                    member_id=member.id, guild_id=guild.id
                )
                if (
                    len(member_data["timestamps"]) == 0
                    and not member_data["has_been_muted"]
                ):
                    member.addons.pop(super().__class__.__name__)
                    await self.anti_spam_handler.cache.set_member(member)

    def get_user_count(self, message: discord.Message) -> int:
        if not isinstance(message, discord.Message):
            raise TypeError("Expected message of type: discord.Message")

        if not message.guild:
            raise MemberNotFound("Can't find user's from dm's")

        member_id = message.author.id
        guild_id = message.guild.id

        try:
            member_data = await self.member_tracking.get_member_data(
                member_id, guild_id
            )
        except (MemberNotFound, GuildNotFound):
            raise MemberNotFound from None

        self.remove_outdated_timestamps(
            guild_id=guild_id, member_id=member_id, data=member_data["timestamps"]
        )

        member_data = await self.member_tracking.get_member_data(member_id, guild_id)

        return len(member_data["timestamps"])

    def remove_outdated_timestamps(
        self, data: typing.List, member_id: int, guild_id: int
    ):
        current_time = datetime.datetime.now(datetime.timezone.utc)

        def _is_still_valid(timestamp):
            difference = current_time - timestamp
            offset = datetime.timedelta(
                milliseconds=await self._get_guild_valid_interval(guild_id=guild_id)
            )

            if difference >= offset:
                return False
            return True

        current_timestamps = []

        member_data = await self.member_tracking.get_member_data(member_id, guild_id)

        for timestamp in member_data["timestamps"]:
            if _is_still_valid(timestamp):
                current_timestamps.append(timestamp)

        member_data["timestamps"] = deepcopy(current_timestamps)
        await self.member_tracking.set_member_data(member_id, guild_id, member_data)
