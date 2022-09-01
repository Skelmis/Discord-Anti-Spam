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
import asyncio
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, AsyncIterable, Dict, List

import pytz
from attr import asdict
from motor.motor_asyncio import AsyncIOMotorClient

from antispam import Options
from antispam.abc import Cache
from antispam.caches.mongo.document import Document
from antispam.dataclasses import Guild, Member, Message
from antispam.enums import ResetType
from antispam.exceptions import GuildNotFound, MemberNotFound

if TYPE_CHECKING:  # pragma: no cover
    from antispam import AntiSpamHandler

log = logging.getLogger(__name__)


class MongoCache(Cache):
    """
    A cache backend built to use MongoDB.

    Parameters
    ----------
    handler: AntiSpamHandler
        The AntiSpamHandler instance
    connection_url: str
        Your MongoDB connection url
    database_name: str, Optional
        The optional name of your collection.

        Defaults to antispam
    """

    def __init__(self, handler, connection_url, database_name=None):
        self.handler: "AntiSpamHandler" = handler
        self.database_name = database_name or "antispam"

        self.__mongo = AsyncIOMotorClient(connection_url)
        self.db = self.__mongo[self.database_name]

        self.guilds: Document = Document(self.db, "antispam_guilds", converter=Guild)
        self.members: Document = Document(self.db, "antispam_members", converter=Member)

        log.info("Cache instance ready to roll.")

    async def get_guild(self, guild_id: int) -> Guild:
        log.debug("Attempting to return cached Guild(id=%s)", guild_id)
        guild: Guild = await self.guilds.find({"id": guild_id})

        # This is a dict here actually
        if not guild:
            raise GuildNotFound

        guild.options = Options(**guild.options)  # type: ignore
        members: List[Member] = await self.members.find_many_by_custom(
            {"guild_id": guild_id}
        )
        for member in members:
            messages: List[Message] = []
            for dict_message in member.messages:
                dict_message: dict = dict_message
                msg = Message(**dict_message)
                msg.creation_time = msg.creation_time.replace(tzinfo=pytz.UTC)
                messages.append(msg)
            member.messages = messages
            guild.members[member.id] = member

        return guild

    async def set_guild(self, guild: Guild) -> None:
        log.debug("Attempting to set Guild(id=%s)", guild.id)
        guild = deepcopy(guild)

        await self._delete_members_for_guild(guild.id)

        # Since self.members exists
        members: List[Member] = list(guild.members.values())
        guild.members = {}

        iters = [self.set_member(m) for m in members]
        await asyncio.gather(*iters)
        await self.guilds.upsert({"id": guild.id}, asdict(guild, recurse=True))

    async def delete_guild(self, guild_id: int) -> None:
        log.debug("Attempting to delete Guild(id=%s)", guild_id)
        await self.guilds.delete({"id": guild_id})
        await self.members.delete({"guild_id": guild_id})

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        log.debug(
            "Attempting to return a cached Member(id=%s) for Guild(id=%s)",
            member_id,
            guild_id,
        )
        member: Member = await self.members.find(
            {"id": member_id, "guild_id": guild_id}
        )
        if not member:
            raise MemberNotFound

        messages: List[Message] = []
        for dict_message in member.messages:
            dict_message: dict = dict_message
            msg = Message(**dict_message)
            msg.creation_time = msg.creation_time.replace(tzinfo=pytz.UTC)
            messages.append(msg)
        member.messages = messages

        return member

    async def set_member(self, member: Member) -> None:
        log.debug(
            "Attempting to cache Member(id=%s) for Guild(id=%s)",
            member.id,
            member.guild_id,
        )
        if not await self._guild_exists(member.guild_id):
            await self.set_guild(Guild(member.guild_id, options=self.handler.options))

        member_dict: Dict = asdict(member, recurse=True)
        await self.members.upsert_custom(
            {"id": member.id, "guild_id": member.guild_id}, member_dict
        )

    async def delete_member(self, member_id: int, guild_id: int) -> None:
        log.debug(
            "Attempting to delete Member(id=%s) in Guild(id=%s)", member_id, guild_id
        )
        await self.members.delete({"id": member_id, "guild_id": guild_id})

    async def add_message(self, message: Message) -> None:
        log.debug(
            "Attempting to add a Message(id=%s) to Member(id=%s) in Guild(id=%s)",
            message.id,
            message.author_id,
            message.guild_id,
        )
        member: Member = await self.members.find(
            {"id": message.author_id, "guild_id": message.guild_id}
        )
        if not member:
            member = Member(message.author_id, guild_id=message.guild_id)

        member.messages.append(message)
        await self.set_member(member)

    async def reset_member_count(
        self, member_id: int, guild_id: int, reset_type: ResetType
    ) -> None:
        log.debug(
            "Attempting to reset counts on Member(id=%s) in Guild(id=%s) with type %s",
            member_id,
            guild_id,
            reset_type.name,
        )
        member: Member = await self.members.find(
            {"id": member_id, "guild_id": guild_id}
        )
        if not member:
            return None

        if reset_type == ResetType.KICK_COUNTER:
            member.kick_count = 0
        else:
            member.warn_count = 0

        await self.set_member(member)

    async def get_all_members(self, guild_id: int) -> AsyncIterable[Member]:
        log.debug("Yielding all cached members for Guild(id=%s)", guild_id)
        if not await self._guild_exists(guild_id):
            raise GuildNotFound

        members = await self.members.find_many_by_custom({"guild_id": guild_id})
        for member in members:
            yield member

    async def get_all_guilds(self) -> AsyncIterable[Guild]:
        log.debug("Yielding all cached guilds")
        guilds = await self.guilds.get_all()
        for guild in guilds:
            yield guild

    async def drop(self) -> None:
        log.warning("Cache was just dropped")
        await self.__mongo.drop_database("antispam_guilds")
        await self.__mongo.drop_database("antispam_members")

    async def _guild_exists(self, guild_id: int) -> True:
        """A guild existence check"""
        r_1 = await self.guilds.find({"id": guild_id})
        return bool(r_1)

    async def _delete_members_for_guild(self, guild_id: int):
        await self.members.delete({"guild_id": guild_id})
