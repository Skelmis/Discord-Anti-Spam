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
import logging
from typing import AsyncIterable

from antispam import dataclasses, exceptions
from antispam.abc import Cache
from antispam.enums import ResetType

log = logging.getLogger(__name__)


class MemoryCache(Cache):
    def __init__(self, handler):
        self.handler = handler
        self.cache = {}
        log.info("Cache instance ready to roll.")

    async def initialize(self, *args, **kwargs) -> None:
        return await super().initialize(*args, **kwargs)

    async def get_guild(self, guild_id: int) -> dataclasses.Guild:
        log.debug("Attempting to return cached Guild(id=%s)", guild_id)
        try:
            return self.cache[guild_id]
        except KeyError:
            raise exceptions.GuildNotFound from None

    async def set_guild(self, guild: dataclasses.Guild) -> None:
        log.debug("Attempting to set Guild(id=%s)", guild.id)
        self.cache[guild.id] = guild

    async def delete_guild(self, guild_id: int) -> None:
        log.debug("Attempting to delete Guild(id=%s)", guild_id)
        self.cache.pop(guild_id, None)

    async def get_member(self, member_id: int, guild_id: int) -> dataclasses.Member:
        log.debug(
            "Attempting to return a cached Member(id=%s) for Guild(id=%s)",
            member_id,
            guild_id,
        )
        guild = await self.get_guild(guild_id)

        try:
            return guild.members[member_id]
        except KeyError:
            raise exceptions.MemberNotFound from None

    async def set_member(self, member: dataclasses.Member) -> None:
        log.debug(
            "Attempting to cache Member(id=%s) for Guild(id=%s)",
            member.id,
            member.guild_id,
        )
        try:
            guild = await self.get_guild(member.guild_id)
        except exceptions.GuildNotFound:
            guild = dataclasses.Guild(id=member.guild_id, options=self.handler.options)

        guild.members[member.id] = member
        await self.set_guild(guild)

    async def delete_member(self, member_id: int, guild_id: int) -> None:
        log.debug(
            "Attempting to delete Member(id=%s) in Guild(id=%s)", member_id, guild_id
        )
        try:
            guild = await self.get_guild(guild_id)
        except exceptions.GuildNotFound:
            return

        try:
            guild.members.pop(member_id)
        except KeyError:
            return

        await self.set_guild(guild)

    async def add_message(self, message: dataclasses.Message) -> None:
        log.debug(
            "Attempting to add a Message(id=%s) to Member(id=%s) in Guild(id=%s)",
            message.id,
            message.author_id,
            message.guild_id,
        )
        try:
            member = await self.get_member(
                member_id=message.author_id, guild_id=message.guild_id
            )
        except exceptions.GuildNotFound:
            member = dataclasses.Member(id=message.author_id, guild_id=message.guild_id)
            guild = dataclasses.Guild(id=message.guild_id, options=self.handler.options)
            guild.members[member.id] = member

            await self.set_guild(guild)

        except exceptions.MemberNotFound:
            guild = await self.get_guild(message.guild_id)

            member = dataclasses.Member(id=message.author_id, guild_id=message.guild_id)
            guild.members[member.id] = member

            await self.set_guild(guild)

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
            member = await self.get_member(member_id, guild_id)
            if reset_type == ResetType.KICK_COUNTER:
                member.kick_count = 0
            # elif reset_type == ResetType.WARN_COUNTER:
            else:
                member.warn_count = 0

            await self.set_member(member)

        except (exceptions.MemberNotFound, exceptions.GuildNotFound):
            # This is fine
            return

    async def get_all_members(
        self, guild_id: int
    ) -> AsyncIterable[dataclasses.Member]:  # noqa
        log.debug("Yielding all cached members for Guild(id=%s)", guild_id)
        guilds = await self.get_guild(guild_id=guild_id)
        for member in guilds.members.values():
            yield member

    async def get_all_guilds(self) -> AsyncIterable[dataclasses.Guild]:  # noqa
        log.debug("Yielding all cached guilds")
        for guild in self.cache.values():
            yield guild

    async def drop(self) -> None:
        log.warning("Cache was just dropped")
        self.cache = {}
