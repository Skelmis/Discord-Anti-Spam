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
from typing import AsyncIterable, List, Optional, Protocol, Union, runtime_checkable

from antispam.dataclasses import Guild, Member, Message
from antispam.dataclasses.propagate_data import PropagateData
from antispam.enums import ResetType


@runtime_checkable
class Cache(Protocol):
    """A generic Protocol for any Cache to implement"""

    def __init__(self, handler) -> None:
        """Stores the handler for later option usage"""
        self.handler = handler

    async def initialize(self, *args, **kwargs) -> None:
        """
        This method gets called once when the AntiSpamHandler
        init() method gets called to allow for setting up
        connections, etc

        Notes
        -----
        This is not required.
        """
        pass

    async def get_guild(self, guild_id: int) -> Guild:
        """Fetch a Guild dataclass populated with members

        Parameters
        ----------
        guild_id : int
            The id of the Guild to retrieve from cache

        Raises
        ------
        GuildNotFound
            A Guild could not be found in the cache
            with the given id
        """
        raise NotImplementedError

    async def set_guild(self, guild: Guild) -> None:
        """
        Stores a Guild in the cache

        This is essentially a UPSERT operation

        Parameters
        ----------
        guild : Guild
            The Guild that needs to be stored

        Warnings
        --------
        This method should be idempotent.

        The passed guild object should not
        experience a change to the callee.
        """
        raise NotImplementedError

    async def delete_guild(self, guild_id: int) -> None:
        """
        Removes a guild from the cache.
        This should also remove all members.

        Parameters
        ----------
        guild_id : int
            The id of the guild we wish to remove

        Notes
        -----
        This fails silently.
        """
        raise NotImplementedError

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        """Fetch a Member dataclass populated with messages

        Parameters
        ----------
        member_id : int
            The id of the member to fetch from cache
        guild_id : int
            The id of the guild this member is associated with

        Raises
        ------
        MemberNotFound
            This Member could not be found on the associated
            Guild within the internal cache
        GuildNotFound
            The relevant guild could not be found
        """
        raise NotImplementedError

    async def set_member(self, member: Member) -> None:
        """
        Stores a Member internally and attaches them
        to a Guild, creating the Guild silently if required

        Essentially an UPSERT operation

        Parameters
        ----------
        member : Member
            The Member we want to cache

        Warnings
        --------
        This method should be idempotent.

        The passed member object should not
        experience a change to the callee.
        """
        raise NotImplementedError

    async def delete_member(self, member_id: int, guild_id: int) -> None:
        """
        Removes a member from the cache.

        Parameters
        ----------
        member_id : int
            The id of the member we wish to remove
        guild_id : int
            The guild this member is in

        Notes
        -----
        This fails silently.
        """
        raise NotImplementedError

    async def add_message(self, message: Message) -> None:
        """
        Adds a Message to the relevant Member,
        creating the Guild/Member if they don't exist

        Parameters
        ----------
        message : Message
            The Message to add to the internal cache

        Notes
        -----
        This should silently create any Guild's/Member's
        required to fulfil this transaction
        """
        raise NotImplementedError

    async def reset_member_count(
        self, member_id: int, guild_id: int, reset_type: ResetType
    ) -> None:
        """
        Reset the chosen enum type back to the default value

        Parameters
        ----------
        member_id : int
            The Member to reset
        guild_id : int
            The guild this member is in
        reset_type : ResetType
            An enum denoting the type of reset

        Notes
        -----
        This shouldn't raise an error if the member doesn't exist.
        """
        raise NotImplementedError

    async def get_all_guilds(self) -> AsyncIterable[Guild]:
        """
        Returns a generator containing all cached guilds

        Yields
        ------
        Guild
            A generator of all stored guilds
        """

    async def get_all_members(self, guild_id: int) -> AsyncIterable[Member]:
        """
        Fetches all members within a guild and returns
        them within a generator

        Parameters
        ----------
        guild_id : int
            The guild we want members in

        Yields
        ------
        Member
            All members in the given guild

        Raises
        ------
        GuildNotFound
            The given guild was not found
        """

    async def drop(self) -> None:
        """
        Drops the entire cache,
        deleting everything contained within.
        """
        raise NotImplementedError
