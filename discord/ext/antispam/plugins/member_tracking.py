from discord.ext.antispam.exceptions import MemberNotFound, GuildNotFound
from discord.ext.antispam.dataclasses import Guild, Member

from discord.ext.antispam.abc import Cache

from discord.ext.antispam import AntiSpamHandler


class MemberTracking:
    """
    This class handles all data storage. You should simply refer
    to the methods in this class as your means off interacting with
    the internal cache
    """

    def __init__(self, handler: AntiSpamHandler, caller):
        """

        Parameters
        ----------
        handler : AntiSpamHandler
            Your AntiSpamHandler instance
        caller : class
            `self`, from the class using this class
        """
        self.handler = handler
        self.cache = handler.cache
        self.key = caller.__class__.__name__

    async def get_member_data(self, guild_id: int, member_id: int) -> dict:
        """
        Returns a dictionary of data this caller is allowed to
        access and store how they please

        Parameters
        ----------
        guild_id : int
            The guild for the user we want
        member_id : int
            The user we want to get data for

        Returns
        -------
        dict
            A dictionary of stored data on this member
            which has been stored by this class

        Raises
        ------
        MemberNotFound
            The given user/guild could not be found internally
        """
        try:
            guild = await self.cache.get_guild(guild_id=guild_id)
        except GuildNotFound:
            raise MemberNotFound from None

        try:
            member = guild.members[member_id]
        except KeyError:
            raise MemberNotFound

        try:
            addon_data = member.addons[self.key]
        except KeyError:
            addon_data = {}
            member.addons[self.key] = addon_data
            await self.cache.set_member(member)

        return addon_data

    async def set_member_data(
        self, guild_id: int, member_id: int, addon_data: dict
    ) -> None:
        """
        Stores a member's data within a guild

        Parameters
        ----------
        guild_id : int
            The guild to add this user's
            data into
        member_id : int
            The user's id to store
        addon_data : dict
            The data to store

        Notes
        -----
        Silently creates the required
        Guild / Member objects as needed
        """
        try:
            guild = await self.cache.get_guild(guild_id=guild_id)
        except GuildNotFound:
            # Create the guild, and store it
            guild = Guild(id=guild_id, options=self.handler.options)
            guild.members[member_id] = Member(id=member_id)
            await self.cache.set_guild(guild)

        # Get/create the member
        try:
            member = guild.members[member_id]
        except KeyError:
            member = Member(id=member_id)

        member.addons[self.key] = addon_data
        guild.members[member_id] = member
        await self.cache.set_member(member)

    async def get_guild_data(self, guild_id: int) -> dict:
        """
        Get a dictionary of all data for this guild that
        was stored by this class

        Parameters
        ----------
        guild_id : int
            The guild to fetch

        Returns
        -------
        GuildNotFound
            The given guild could not be found
            in the cache
        """
        guild = await self.cache.get_guild(guild_id=guild_id)
        try:
            addon_data = guild.addons[self.key]
        except KeyError:
            addon_data = {}
            guild.addons[self.key] = addon_data
            await self.cache.set_guild(guild)

        return addon_data

    async def set_guild_data(self, guild_id: int, addon_data: dict) -> None:
        """
        Stores the given addon data dictionary within the guilds cache

        Parameters
        ----------
        guild_id : int
            The guild to store this on
        addon_data : dict
            The data to store on this guild

        Notes
        -----
        Silently creates a new Guild as required
        """
        try:
            guild = await self.cache.get_guild(guild_id=guild_id)
        except GuildNotFound:
            guild = Guild(id=guild_id, options=self.handler.options)

        guild.addons[self.key] = addon_data
        await self.cache.set_guild(guild)
