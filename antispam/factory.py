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
from copy import deepcopy

from antispam.abc import Cache
from antispam.dataclasses import Guild, Member, Message, Options

log = logging.getLogger(__name__)


class FactoryBuilder:
    """A factory to build dataclasses from dictionaries"""

    @staticmethod
    def create_guild_from_dict(guild_data: dict) -> Guild:
        guild: Guild = Guild(
            id=guild_data["id"], options=Options(**guild_data["options"])
        )

        for member in guild_data["members"]:
            guild.members[member["id"]] = FactoryBuilder.create_member_from_dict(member)

        log.info("Created Guild(id=%s) from dict", guild.id)

        return guild

    @staticmethod
    def create_member_from_dict(member_data) -> Member:
        member: Member = Member(id=member_data["id"], guild_id=member_data["guild_id"])
        member.internal_is_in_guild = member_data["is_in_guild"]
        member.warn_count = member_data["warn_count"]
        member.kick_count = member_data["kick_count"]
        member.duplicate_counter = member_data["duplicate_count"]
        member.duplicate_channel_counter_dict = deepcopy(
            member_data["duplicate_channel_counter_dict"]
        )

        for message_data in member_data["messages"]:
            member.messages.append(
                FactoryBuilder.create_message_from_dict(message_data)
            )

        log.info("Created Member(id=%s) from dict", member.id)

        return member

    @staticmethod
    def create_message_from_dict(message_data) -> Message:
        message = Message(
            id=message_data["id"],
            content=message_data["content"],
            guild_id=message_data["guild_id"],
            author_id=message_data["author_id"],
            channel_id=message_data["channel_id"],
        )
        message.is_duplicate = message_data["is_duplicate"]
        message.creation_time = datetime.datetime.strptime(
            message_data["creation_time"], "%f:%S:%M:%H:%d:%m:%Y"
        )
        log.info("Created Message(id=%s) from dict", message.id)

        return message

    @staticmethod
    def clean_old_messages(member: Member, current_time, options):
        def _is_still_valid(message_obj):
            """
            Given a message, figure out if it hasn't
            expired yet based on timestamps
            """
            difference = current_time - message_obj.creation_time
            offset = datetime.timedelta(milliseconds=options.message_interval)

            if difference >= offset:
                return False
            return True

        current_messages = []
        outstanding_messages = []

        for message in member.messages:
            if _is_still_valid(message):
                current_messages.append(message)
            else:
                outstanding_messages.append(message)

        member.messages = current_messages

    @staticmethod
    async def get_all_members_as_list(cache: Cache, guild_id: int):
        """
        Given a cache, evaluate the async
        generator in order to return a list

        Parameters
        ----------
        cache : Cache
            The cache to use to fetch stuff
        guild_id : int
            The guild to get members from

        Returns
        -------
        List
            A list of all members in the guild

        Raises
        ------
        GuildNotFound
        """
        return [member async for member in cache.get_all_members(guild_id=guild_id)]

    @staticmethod
    async def get_all_guilds_as_list(cache: Cache):
        """
        Given a cache, evaluate the async
        generator in order to return a list

        Parameters
        ----------
        cache : Cache
            The cache to use to fetch stuff

        Returns
        -------
        List
            A list of all cached guilds
        """
        return [guild async for guild in cache.get_all_guilds()]
