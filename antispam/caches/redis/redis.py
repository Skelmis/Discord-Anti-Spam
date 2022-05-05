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

from typing import TYPE_CHECKING, List, AsyncIterable

from attr import asdict

import orjson as json

from antispam.abc import Cache
from antispam.exceptions import GuildNotFound, MemberNotFound
from antispam.dataclasses import Message, Member, Guild, Options
from antispam.enums import ResetType

if TYPE_CHECKING:
    from redis import asyncio as aioredis

    from antispam import AntiSpamHandler


class RedisCache(Cache):
    """Not implemented lol"""

    def __init__(self, handler: AntiSpamHandler, redis: aioredis.Redis):
        self.redis: aioredis.Redis = redis
        self.handler: AntiSpamHandler = handler

    async def get_guild(self, guild_id: int) -> Guild:
        resp = await self.redis.get(f"GUILD:{guild_id}")
        if not resp:
            raise GuildNotFound

        resp = resp.decode("utf-8")
        as_json = json.loads(resp)

        guild: Guild = Guild(**as_json)
        # This is actually a dict here
        guild.options = Options(**guild.options)  # type: ignore

        guild_members: List[Member] = []
        for member_id in guild.members:  # type: ignore
            member: Member = await self.get_member(member_id, guild_id)
            guild_members.append(member)

        guild.members = guild_members

        return guild

    async def set_guild(self, guild: Guild) -> None:
        # Store members separate
        for member in guild.members.values():
            await self.set_member(member)

        guild.members = [member.id for member in guild.members.values()]
        as_json = json.dumps(asdict(guild, recurse=True))
        await self.redis.set(f"GUILD:{guild.id}", as_json)

    async def delete_guild(self, guild_id: int) -> None:
        await self.redis.delete(f"GUILD:{guild_id}")

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        resp = await self.redis.get(f"MEMBER:{member_id}:{guild_id}")
        if not resp:
            raise MemberNotFound

        resp = resp.decode("utf-8")
        as_json = json.loads(resp)

        member: Member = Member(**as_json)

        messages: List[Message] = []
        for message in member.messages:
            messages.append(Message(**message))  # type: ignore

        member.messages = messages

        return member

    async def set_member(self, member: Member) -> None:
        as_json = json.dumps(asdict(member, recurse=True))
        await self.redis.set(f"MEMBER:{member.guild_id}:{member.id}", as_json)

    async def delete_member(self, member_id: int, guild_id: int) -> None:
        await self.redis.delete(f"MEMBER:{guild_id}:{member_id}")

    async def add_message(self, message: Message) -> None:
        try:
            member: Member = await self.get_member(message.author_id, message.guild_id)
        except (MemberNotFound, GuildNotFound):
            member = Member(message.author_id, guild_id=message.guild_id)

        member.messages.append(message)
        await self.set_member(member)

    async def reset_member_count(
        self, member_id: int, guild_id: int, reset_type: ResetType
    ) -> None:
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
        await self.redis.flushdb(asynchronous=True)

    async def get_all_guilds(self) -> AsyncIterable[Guild]:
        keys: List[bytes] = await self.redis.keys("GUILD:*")
        for key in keys:
            yield await self.get_guild(int(key.decode("utf-8").split(":")[1]))

    async def get_all_members(self, guild_id: int) -> AsyncIterable[Member]:
        keys: List[bytes] = await self.redis.keys(f"MEMBER:{guild_id}:*")
        for key in keys:
            yield await self.get_member(
                int(key.decode("utf-8").split(":")[2]), guild_id
            )
