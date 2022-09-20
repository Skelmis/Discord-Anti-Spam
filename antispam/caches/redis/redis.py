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
from __future__ import annotations

import asyncio
import datetime
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, List, AsyncIterable, Dict, cast

from attr import asdict

import orjson as json

from antispam.abc import Cache
from antispam.enums import ResetType
from antispam.exceptions import GuildNotFound, MemberNotFound
from antispam.dataclasses import Message, Member, Guild, Options

if TYPE_CHECKING:
    from redis import asyncio as aioredis

    from antispam import AntiSpamHandler

log = logging.getLogger(__name__)


class RedisCache(Cache):
    """
    A cache backend built to use Redis.

    Parameters
    ----------
    handler: AntiSpamHandler
        The AntiSpamHandler instance
    redis: redis.asyncio.Redis
        Your redis connection instance.
    """

    def __init__(self, handler: AntiSpamHandler, redis: aioredis.Redis):
        self.redis: aioredis.Redis = redis
        self.handler: AntiSpamHandler = handler

    async def get_guild(self, guild_id: int) -> Guild:
        log.debug("Attempting to return cached Guild(id=%s)", guild_id)
        resp = await self.redis.get(f"GUILD:{guild_id}")
        if not resp:
            raise GuildNotFound

        as_json = json.loads(resp.decode("utf-8"))
        guild: Guild = Guild(**as_json)
        # This is actually a dict here
        guild.options = cast(dict, guild.options)
        guild.options = Options(**guild.options)

        guild_members: Dict[int, Member] = {}
        async for member in self.get_all_members(guild_id):
            guild_members[member.id] = member

        guild.members = guild_members
        return guild

    async def set_guild(self, guild: Guild) -> None:
        log.debug("Attempting to set Guild(id=%s)", guild.id)
        guild = deepcopy(guild)  # Ensure idempotent

        # We do this to clear the 'old' guilds members
        await self._delete_members_for_guild(guild.id)

        members: List[Member] = list(guild.members.values())
        guild.members = {}
        iters = [self.set_member(m) for m in members]
        await asyncio.gather(*iters)

        as_json = json.dumps(asdict(guild, recurse=True))
        await self.redis.set(f"GUILD:{guild.id}", as_json)

    async def delete_guild(self, guild_id: int) -> None:
        log.debug("Attempting to delete Guild(id=%s)", guild_id)
        await self._delete_members_for_guild(guild_id)
        await self.redis.delete(f"GUILD:{guild_id}")

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        log.debug(
            "Attempting to return a cached Member(id=%s) for Guild(id=%s)",
            member_id,
            guild_id,
        )
        resp = await self.redis.get(f"MEMBER:{guild_id}:{member_id}")
        if not resp:
            raise MemberNotFound

        as_json = json.loads(resp.decode("utf-8"))
        member: Member = Member(**as_json)

        messages: List[Message] = []
        member.messages = cast(list, member.messages)
        for message in member.messages:
            message = Message(**message)
            message.creation_time = datetime.datetime.fromisoformat(
                message.creation_time  # type: ignore
            )
            messages.append(message)

        member.messages = messages
        return member

    async def set_member(self, member: Member) -> None:
        log.debug(
            "Attempting to cache Member(id=%s) for Guild(id=%s)",
            member.id,
            member.guild_id,
        )
        if not await self._does_guild_exist(member.guild_id):
            guild = Guild(id=member.guild_id, options=self.handler.options)
            guild.members = {}
            guild_as_json = json.dumps(asdict(guild, recurse=True))
            await self.redis.set(f"GUILD:{guild.id}", guild_as_json)

        as_json = json.dumps(asdict(member, recurse=True))
        await self.redis.set(f"MEMBER:{member.guild_id}:{member.id}", as_json)

    async def delete_member(self, member_id: int, guild_id: int) -> None:
        log.debug(
            "Attempting to delete Member(id=%s) in Guild(id=%s)", member_id, guild_id
        )
        await self.redis.delete(f"MEMBER:{guild_id}:{member_id}")

    async def add_message(self, message: Message) -> None:
        log.debug(
            "Attempting to add a Message(id=%s) to Member(id=%s) in Guild(id=%s)",
            message.id,
            message.author_id,
            message.guild_id,
        )
        try:
            member: Member = await self.get_member(message.author_id, message.guild_id)
        except (MemberNotFound, GuildNotFound):
            member: Member = Member(message.author_id, guild_id=message.guild_id)

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
        try:
            member: Member = await self.get_member(member_id, guild_id)
        except (MemberNotFound, GuildNotFound):
            return

        if reset_type == ResetType.KICK_COUNTER:
            member.kick_count = 0
        else:
            member.warn_count = 0

        await self.set_member(member)

    async def drop(self) -> None:
        log.warning("Cache was just dropped")
        async for guild in self.get_all_guilds():
            await self.delete_guild(guild.id)

    async def get_all_guilds(self) -> AsyncIterable[Guild]:
        log.debug("Yielding all cached guilds")
        keys: List[bytes] = await self.redis.keys("GUILD:*")
        for key in keys:
            key = key.decode("utf-8").split(":")[1]
            yield await self.get_guild(int(key))

    async def get_all_members(self, guild_id: int) -> AsyncIterable[Member]:
        log.debug("Yielding all cached members for Guild(id=%s)", guild_id)
        if not await self._does_guild_exist(guild_id):
            raise GuildNotFound

        async for member in self._get_all_members(guild_id):
            yield member

    async def _get_all_members(self, guild_id: int) -> AsyncIterable[Member]:
        """This exists so we don't need to raise GuildNotFound when used internally."""
        keys: List[bytes] = await self.redis.keys(f"MEMBER:{guild_id}:*")
        for key in keys:
            key = key.decode("utf-8").split(":")[2]
            yield await self.get_member(int(key), guild_id)

    async def _does_guild_exist(self, guild_id: int) -> bool:
        resp = await self.redis.get(f"GUILD:{guild_id}")
        return bool(resp)

    async def _delete_members_for_guild(self, guild_id: int):
        async for member in self._get_all_members(guild_id):
            await self.delete_member(member.id, member.guild_id)
