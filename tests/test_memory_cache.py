import pytest

from discord.ext.antispam import GuildNotFound, Options, MemberNotFound  # noqa

from discord.ext.antispam.dataclasses import Guild, Member, Message  # noqa
from .fixtures import create_handler, create_memory_cache, create_bot  # noqa


class TestMemoryCache:
    @pytest.mark.asyncio
    async def test_memory_init(self, create_memory_cache):
        # Coverage
        await create_memory_cache.initialize()

    @pytest.mark.asyncio
    async def test_get_guild(self, create_memory_cache):
        with pytest.raises(GuildNotFound):
            await create_memory_cache.get_guild(1)

        create_memory_cache.cache[1] = 2

        val = await create_memory_cache.get_guild(1)
        assert val == 2

    @pytest.mark.asyncio
    async def test_set_guild(self, create_memory_cache):
        assert create_memory_cache.cache == {}
        await create_memory_cache.set_guild(Guild(1, Options()))
        assert create_memory_cache.cache == {1: Guild(1, Options())}

    @pytest.mark.asyncio
    async def test_get_member(self, create_memory_cache):
        await create_memory_cache.set_guild(Guild(1, Options()))
        with pytest.raises(MemberNotFound):
            await create_memory_cache.get_member(1, 1)

        create_memory_cache.cache[1].members[1] = 2

        val = await create_memory_cache.get_member(1, 1)
        assert val == 2

    @pytest.mark.asyncio
    async def test_set_member(self, create_memory_cache):
        await create_memory_cache.set_member(Member(1, 1))
        await create_memory_cache.set_member(Member(2, 1))

        assert len(create_memory_cache.cache[1].members) == 2

        await create_memory_cache.set_guild(Guild(1, Options()))
        assert len(create_memory_cache.cache[1].members) == 0

        await create_memory_cache.set_member(Member(1, 1))
        assert len(create_memory_cache.cache[1].members) == 1

    @pytest.mark.asyncio
    async def test_add_message_raw(self, create_memory_cache):
        """Test without a pre-filled cache"""
        await create_memory_cache.add_message(Message(1, 2, 3, 4, "Content"))
        assert len(create_memory_cache.cache[3].members) == 1
        assert len(create_memory_cache.cache[3].members[4].messages) == 1

    @pytest.mark.asyncio
    async def test_add_message_filled_guild(self, create_memory_cache):
        """Test with an existing guild"""
        await create_memory_cache.set_guild(Guild(3, Options()))
        await create_memory_cache.add_message(Message(1, 2, 3, 4, "Content"))
        assert len(create_memory_cache.cache[3].members) == 1
        assert len(create_memory_cache.cache[3].members[4].messages) == 1

    @pytest.mark.asyncio
    async def test_add_message_filled(self, create_memory_cache):
        """Test with a pre-filled member"""
        await create_memory_cache.set_member(Member(4, 3))
        await create_memory_cache.add_message(Message(1, 2, 3, 4, "Content"))

        assert len(create_memory_cache.cache[3].members) == 1
        assert len(create_memory_cache.cache[3].members[4].messages) == 1
