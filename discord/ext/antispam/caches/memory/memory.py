from ...abc import Cache
from ...dataclasses import Message, Member, Guild


class Memory(Cache):
    """pass"""

    async def initialize(self, *args, **kwargs) -> None:
        return await super().initialize(*args, **kwargs)

    async def get_guild(self, guild_id: int) -> Guild:
        return await super().get_guild(guild_id)

    async def set_guild(self, guild: Guild) -> None:
        return await super().set_guild(guild)

    async def get_member(self, member_id: int, guild_id: int) -> Member:
        return await super().get_member(member_id, guild_id)

    async def set_member(self, member: Member) -> None:
        return await super().set_member(member)

    async def add_message(self, message: Message) -> None:
        return await super().add_message(message)
