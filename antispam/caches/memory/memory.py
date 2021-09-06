from typing import List

from ...abc import Cache
from ...dataclasses import Message, Member, Guild
from ...enums import ResetType
from ...exceptions import GuildNotFound, MemberNotFound


class MemoryCache(Cache):
    def __init__(self, handler):
        self.handler = handler
        self.cache = {}

    async def initialize(self, *args, **kwargs) -> None:
        return await super().initialize(*args, **kwargs)

    async def get_guild(self, guild_id: int) -> Guild:
        try:
            return self.cache[guild_id]
        except KeyError:
            raise GuildNotFound from None

    async def set_guild(self, guild: Guild) -> None:
        self.cache[guild.id] = guild

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        guild = await self.get_guild(guild_id)

        try:
            return guild.members[member_id]
        except KeyError:
            raise MemberNotFound from None

    async def set_member(self, member: Member) -> None:
        try:
            guild = await self.get_guild(member.guild_id)
        except GuildNotFound:
            guild = Guild(id=member.guild_id, options=self.handler.options)

        guild.members[member.id] = member
        await self.set_guild(guild)

    async def add_message(self, message: Message) -> None:
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

    async def get_all_members(self, guild_id: int) -> List[Member]:
        guild = await self.get_guild(guild_id=guild_id)
        return list(guild.members.values())

    async def get_all_guilds(self) -> List[Guild]:
        return list(self.cache.values())