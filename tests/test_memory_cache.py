import pytest

from antispam import GuildNotFound, MemberNotFound, Options
from antispam.dataclasses import Guild, Member, Message
from antispam.enums import ResetType
from antispam.factory import FactoryBuilder


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

    @pytest.mark.asyncio
    async def test_reset_member_count(self, create_memory_cache):
        await create_memory_cache.set_member(Member(1, 1, kick_count=1, warn_count=2))

        member = await create_memory_cache.get_member(1, 1)
        assert (member.kick_count, member.warn_count) == (1, 2)

        await create_memory_cache.reset_member_count(1, 1, ResetType.KICK_COUNTER)

        member = await create_memory_cache.get_member(1, 1)
        assert (member.kick_count, member.warn_count) == (0, 2)

        await create_memory_cache.reset_member_count(1, 1, ResetType.WARN_COUNTER)

        member = await create_memory_cache.get_member(1, 1)
        assert (member.kick_count, member.warn_count) == (0, 0)

    @pytest.mark.asyncio
    async def test_get_all_members(self, create_memory_cache):
        with pytest.raises(GuildNotFound):
            await FactoryBuilder.get_all_members_as_list(create_memory_cache, 1)

        await create_memory_cache.set_member(Member(1, 1))
        await create_memory_cache.set_member(Member(2, 1))
        await create_memory_cache.set_member(Member(3, 1))

        members = await FactoryBuilder.get_all_members_as_list(create_memory_cache, 1)
        assert len(members) == 3
        assert members == [Member(1, 1), Member(2, 1), Member(3, 1)]

    @pytest.mark.asyncio
    async def test_get_all_guilds(self, create_memory_cache):
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_memory_cache)
        assert len(guilds) == 0

        await create_memory_cache.set_guild(Guild(1, Options()))
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_memory_cache)
        assert len(guilds) == 1

        await create_memory_cache.set_guild(Guild(2, Options()))
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_memory_cache)
        assert len(guilds) == 2
        assert guilds == [Guild(1, Options()), Guild(2, Options())]

    @pytest.mark.asyncio
    async def test_delete_guild(self, create_memory_cache):
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_memory_cache)
        assert len(guilds) == 0

        await create_memory_cache.delete_guild(1)

        guilds = await FactoryBuilder.get_all_guilds_as_list(create_memory_cache)
        assert len(guilds) == 0

        await create_memory_cache.set_guild(Guild(1))

        guilds = await FactoryBuilder.get_all_guilds_as_list(create_memory_cache)
        assert len(guilds) == 1

        await create_memory_cache.delete_guild(1)

        guilds = await FactoryBuilder.get_all_guilds_as_list(create_memory_cache)
        assert len(guilds) == 0

    @pytest.mark.asyncio
    async def test_delete_member(self, create_memory_cache):
        await create_memory_cache.delete_member(1, 2)
        await create_memory_cache.set_guild(Guild(2))
        await create_memory_cache.delete_member(1, 2)

        guild = await create_memory_cache.get_guild(2)
        guild.members[1] = Member(1, 2)
        await create_memory_cache.set_guild(guild)
        assert len(guild.members) == 1

        await create_memory_cache.delete_member(1, 2)
        g = await create_memory_cache.get_guild(2)
        assert len(g.members) == 0
