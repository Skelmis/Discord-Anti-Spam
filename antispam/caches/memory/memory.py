import logging
from typing import List, Iterator

from ...abc import Cache
from ...dataclasses import Message, Member, Guild
from ...enums import ResetType
from ...exceptions import GuildNotFound, MemberNotFound


log = logging.getLogger(__name__)


class MemoryCache(Cache):
    def __init__(self, handler):
        self.handler = handler
        self.cache = {}
        log.info("Cache has been initialized")

    async def initialize(self, *args, **kwargs) -> None:
        return await super().initialize(*args, **kwargs)

    async def get_guild(self, guild_id: int) -> Guild:
        log.debug("Attempting to return cached guild %s", guild_id)
        try:
            return self.cache[guild_id]
        except KeyError:
            raise GuildNotFound from None

    async def set_guild(self, guild: Guild) -> None:
        log.debug("Attempting to set guild %s", guild.id)
        self.cache[guild.id] = guild

    async def delete_guild(self, guild_id: int) -> None:
        log.debug("Attempting to delete guild %s", guild_id)
        self.cache.pop(guild_id, None)

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        log.debug(
            "Attempting to return a cached member (%s) for guild %s",
            member_id,
            guild_id,
        )
        guild = await self.get_guild(guild_id)

        try:
            return guild.members[member_id]
        except KeyError:
            raise MemberNotFound from None

    async def set_member(self, member: Member) -> None:
        log.debug(
            "Attempting to cache member %s for guild %s", member.id, member.guild_id
        )
        try:
            guild = await self.get_guild(member.guild_id)
        except GuildNotFound:
            guild = Guild(id=member.guild_id, options=self.handler.options)

        guild.members[member.id] = member
        await self.set_guild(guild)

    async def delete_member(self, member_id: int, guild_id: int) -> None:
        log.debug("Attempting to delete %s in guild %s", member_id, guild_id)
        try:
            guild = await self.get_guild(guild_id)
        except GuildNotFound:
            return

        try:
            guild.members.pop(member_id)
        except KeyError:
            return

        await self.set_guild(guild)

    async def add_message(self, message: Message) -> None:
        log.debug(
            "Attempting to add a message to %s in guild %s",
            message.author_id,
            message.guild_id,
        )
        try:
            member = await self.get_member(
                member_id=message.author_id, guild_id=message.guild_id
            )
        except GuildNotFound:
            member = Member(id=message.author_id, guild_id=message.guild_id)
            guild = Guild(id=message.guild_id, options=self.handler.options)
            guild.members[member.id] = member

            await self.set_guild(guild)

        except MemberNotFound:
            guild = await self.get_guild(message.guild_id)

            member = Member(id=message.author_id, guild_id=message.guild_id)
            guild.members[member.id] = member

            await self.set_guild(guild)

        member.messages.append(message)
        await self.set_member(member)

    async def reset_member_count(
        self, member_id: int, guild_id: int, reset_type: ResetType
    ) -> None:
        log.debug(
            "Attempting to reset %s in guild %s with type %s",
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

        except (MemberNotFound, GuildNotFound):
            # This is fine
            return

    async def get_all_members(self, guild_id: int) -> Iterator[Member]:  # noqa
        log.debug("Yielding all cached members for %s", guild_id)
        guilds = await self.get_guild(guild_id=guild_id)
        for member in guilds.members.values():
            yield member

    async def get_all_guilds(self) -> List[Guild]:  # noqa
        log.debug("Yield all cached guilds")
        for guild in self.cache.values():
            yield guild

    async def drop(self) -> None:
        log.info("Cache was just dropped.")
        self.cache = {}
