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
from typing import Any

from antispam import AntiSpamHandler
from antispam.dataclasses import Guild, Member
from antispam.exceptions import (
    GuildAddonNotFound,
    GuildNotFound,
    MemberAddonNotFound,
    MemberNotFound,
)


class PluginCache:
    """
    This class handles all data storage. You should simply refer
    to the methods in this class as your means of interacting with
    the internal cache
    """

    def __init__(self, handler: AntiSpamHandler, caller):
        """

        Parameters
        ----------
        handler : AntiSpamHandler
            Your AntiSpamHandler instance
        caller : object
            `self`, from the class using this class
        """
        self.handler = handler
        self.cache = handler.cache
        self.key = caller.__class__.__name__

    async def get_member_data(
        self,
        member_id: int,
        guild_id: int,
    ) -> Any:
        """
        Returns a dictionary of data this caller is allowed to
        access and store how they please

        Parameters
        ----------
        member_id : int
            The user we want to get data for
        guild_id : int
            The guild for the user we want

        Returns
        -------
        Any
            Stored data on this member
            which has been stored by this class

        Raises
        ------
        MemberNotFound
            The given user/guild could not be found
            internally or they have no stored data
        """
        guild = await self.cache.get_guild(guild_id=guild_id)

        try:
            member = guild.members[member_id]
        except KeyError:
            raise MemberNotFound

        try:
            addon_data = member.addons[self.key]
        except KeyError:
            # Raise here because the datatype is guaranteed
            raise MemberAddonNotFound

        return addon_data

    async def set_member_data(
        self, member_id: int, guild_id: int, addon_data: Any
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
        addon_data : Any
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
            guild.members[member_id] = Member(id=member_id, guild_id=guild_id)
            await self.cache.set_guild(guild)

        # Get/create the member
        try:
            member = guild.members[member_id]
        except KeyError:
            member = Member(id=member_id, guild_id=guild_id)

        member.addons[self.key] = addon_data
        guild.members[member_id] = member
        await self.cache.set_member(member)

    async def get_guild_data(self, guild_id: int) -> Any:
        """
        Get a dictionary of all data for this guild that
        was stored by this class

        Parameters
        ----------
        guild_id : int
            The guild to fetch

        Returns
        -------
        Any
            The data stored on this

        Raises
        ------
        GuildNotFound
            The given guild could not be found
            in the cache or it has no stored data
        """
        guild = await self.cache.get_guild(guild_id=guild_id)
        try:
            addon_data = guild.addons[self.key]
        except KeyError:
            # Raise since datatype is `Any` and we dunno what to return
            raise GuildAddonNotFound

        return addon_data

    async def set_guild_data(self, guild_id: int, addon_data: Any) -> None:
        """
        Stores the given addon data dictionary within the guilds cache

        Parameters
        ----------
        guild_id : int
            The guild to store this on
        addon_data : Any
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
