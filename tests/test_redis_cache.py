import datetime

import orjson as json

import pytest
from attr import asdict

from antispam import GuildNotFound, MemberNotFound, Options
from antispam.caches.redis import RedisCache
from antispam.dataclasses import Guild, Member, Message
from antispam.enums import ResetType
from antispam.factory import FactoryBuilder


class TestRedisCache:
    @pytest.mark.asyncio
    async def test_redis_init(self, create_redis_cache):
        # Coverage
        await create_redis_cache.initialize()

    @pytest.mark.asyncio
    async def test_get_guild(self, create_redis_cache):
        with pytest.raises(GuildNotFound):
            await create_redis_cache.get_guild(1)

        create_redis_cache.redis.cache["GUILD:1"] = json.dumps(
            asdict(Guild(1), recurse=True)
        )

        val = await create_redis_cache.get_guild(1)
        assert val
        assert isinstance(val, Guild)

    @pytest.mark.asyncio
    async def test_set_guild(self, create_redis_cache):
        assert not create_redis_cache.redis.cache
        await create_redis_cache.set_guild(Guild(1, Options()))
        assert create_redis_cache.redis.cache

    @pytest.mark.asyncio
    async def test_get_member(self, create_redis_cache):
        await create_redis_cache.set_guild(Guild(1, Options()))
        with pytest.raises(MemberNotFound):
            await create_redis_cache.get_member(1, 1)

        await create_redis_cache.set_member(Member(1, 1))

        val = await create_redis_cache.get_member(1, 1)
        assert val
        assert isinstance(val, Member)

    @pytest.mark.asyncio
    async def test_set_member(self, create_redis_cache):
        await create_redis_cache.set_member(Member(1, 1))
        await create_redis_cache.set_member(Member(2, 1))

        r_1 = await create_redis_cache.get_guild(1)
        assert len(r_1.members) == 2

        await create_redis_cache.set_guild(Guild(1, Options()))
        r_2 = await create_redis_cache.get_guild(1)
        assert len(r_2.members) == 0

        await create_redis_cache.set_member(Member(1, 1))

        r_3 = await create_redis_cache.get_guild(1)
        assert len(r_3.members) == 1

    @pytest.mark.asyncio
    async def test_add_message_raw(self, create_redis_cache):
        """Test without a pre-filled cache"""
        await create_redis_cache.add_message(Message(1, 2, 3, 4, "Content"))

        r_1 = await create_redis_cache.get_guild(3)
        assert len(r_1.members) == 1
        assert len(r_1.members[4].messages) == 1

    @pytest.mark.asyncio
    async def test_add_message_filled_guild(self, create_redis_cache):
        """Test with an existing guild"""
        await create_redis_cache.set_guild(Guild(3, Options()))
        await create_redis_cache.add_message(Message(1, 2, 3, 4, "Content"))

        r_1 = await create_redis_cache.get_member(4, 3)
        r_2 = await create_redis_cache.get_guild(3)
        assert len(r_2.members) == 1
        assert len(r_1.messages) == 1

    @pytest.mark.asyncio
    async def test_add_message_filled(self, create_redis_cache):
        """Test with a pre-filled member"""
        await create_redis_cache.set_member(Member(4, 3))
        await create_redis_cache.add_message(Message(1, 2, 3, 4, "Content"))

        r_1 = await create_redis_cache.get_guild(3)
        assert len(r_1.members) == 1
        assert len(r_1.members[4].messages) == 1

    @pytest.mark.asyncio
    async def test_reset_member_count(self, create_redis_cache):
        await create_redis_cache.set_member(Member(1, 1, kick_count=1, warn_count=2))

        member = await create_redis_cache.get_member(1, 1)
        assert (member.kick_count, member.warn_count) == (1, 2)

        await create_redis_cache.reset_member_count(1, 1, ResetType.KICK_COUNTER)

        member = await create_redis_cache.get_member(1, 1)
        assert (member.kick_count, member.warn_count) == (0, 2)

        await create_redis_cache.reset_member_count(1, 1, ResetType.WARN_COUNTER)

        member = await create_redis_cache.get_member(1, 1)
        assert (member.kick_count, member.warn_count) == (0, 0)

    @pytest.mark.asyncio
    async def test_get_all_members(self, create_redis_cache):
        with pytest.raises(GuildNotFound):
            await FactoryBuilder.get_all_members_as_list(create_redis_cache, 1)

        await create_redis_cache.set_member(Member(1, 1))
        await create_redis_cache.set_member(Member(2, 1))
        await create_redis_cache.set_member(Member(3, 1))

        members = await FactoryBuilder.get_all_members_as_list(create_redis_cache, 1)
        assert len(members) == 3
        assert members == [Member(1, 1), Member(2, 1), Member(3, 1)]

    @pytest.mark.asyncio
    async def test_get_all_guilds(self, create_redis_cache):
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_redis_cache)
        assert len(guilds) == 0

        await create_redis_cache.set_guild(Guild(1, Options()))
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_redis_cache)
        assert len(guilds) == 1

        await create_redis_cache.set_guild(Guild(2, Options()))
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_redis_cache)
        assert len(guilds) == 2
        assert guilds == [Guild(1, Options()), Guild(2, Options())]

    @pytest.mark.asyncio
    async def test_delete_guild(self, create_redis_cache):
        guilds = await FactoryBuilder.get_all_guilds_as_list(create_redis_cache)
        assert len(guilds) == 0

        await create_redis_cache.delete_guild(1)

        guilds = await FactoryBuilder.get_all_guilds_as_list(create_redis_cache)
        assert len(guilds) == 0

        await create_redis_cache.set_guild(Guild(1))

        guilds = await FactoryBuilder.get_all_guilds_as_list(create_redis_cache)
        assert len(guilds) == 1

        await create_redis_cache.delete_guild(1)

        guilds = await FactoryBuilder.get_all_guilds_as_list(create_redis_cache)
        assert len(guilds) == 0

    @pytest.mark.asyncio
    async def test_delete_member(self, create_redis_cache):
        await create_redis_cache.delete_member(1, 2)
        await create_redis_cache.set_guild(Guild(2))
        await create_redis_cache.delete_member(1, 2)

        guild = await create_redis_cache.get_guild(2)
        guild.members[1] = Member(1, 2)
        await create_redis_cache.set_guild(guild)
        assert len(guild.members) == 1

        await create_redis_cache.delete_member(1, 2)
        g = await create_redis_cache.get_guild(2)
        assert len(g.members) == 0

    @pytest.mark.asyncio
    async def test_date_serialization(self, create_redis_cache: RedisCache):
        # https://github.com/Skelmis/Discord-Anti-Spam/issues/104
        await create_redis_cache.set_guild(
            Guild(
                1,
                Options(),
                members={
                    1: Member(1, 1, messages=[Message(1, 1, 1, 1, "Hello world")])
                },
            )
        )

        member: Member = await create_redis_cache.get_member(1, 1)
        assert isinstance(member.messages[0].creation_time, datetime.datetime)

    @pytest.mark.asyncio
    async def test_guild_delete_cleans_members(self, create_redis_cache: RedisCache):
        await create_redis_cache.set_guild(
            Guild(
                1,
                Options(),
                members={
                    1: Member(1, 1, messages=[Message(1, 1, 1, 1, "Hello world")])
                },
            )
        )

        await create_redis_cache.delete_guild(1)

        with pytest.raises(GuildNotFound):
            await create_redis_cache.get_guild(1)

        with pytest.raises(MemberNotFound):
            await create_redis_cache.get_member(1, 1)

    @pytest.mark.asyncio
    async def test_set_member_is_idempotent(self, create_redis_cache):
        member = Member(
            3,
            1,
            messages=[
                Message(1, 1, 1, 1, "Hello world"),
                Message(2, 1, 1, 1, "foo bar"),
            ],
        )
        assert isinstance(member.messages[0].creation_time, datetime.datetime)
        await create_redis_cache.set_member(member)
        assert isinstance(member.messages[0].creation_time, datetime.datetime)
