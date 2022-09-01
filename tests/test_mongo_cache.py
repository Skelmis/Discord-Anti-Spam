import datetime

import pytest

from antispam import GuildNotFound, Options, MemberNotFound
from antispam.dataclasses import Guild, Member, Message
from antispam.enums import ResetType


class TestMongoCache:
    @pytest.mark.asyncio
    async def test_get_guild(self, create_mongo_cache):
        """Tests guilds are fetched and converted correct"""
        with pytest.raises(GuildNotFound):
            await create_mongo_cache.get_guild(2)

        r_1 = await create_mongo_cache.get_guild(1)
        assert isinstance(r_1, Guild)
        assert isinstance(r_1.options, Options)
        assert len(r_1.members) == 2

    @pytest.mark.asyncio
    async def test_set_guild(self, create_mongo_cache):
        with pytest.raises(GuildNotFound):
            await create_mongo_cache.get_guild(2)

        set_guild = Guild(2, log_channel_id=12345)
        await create_mongo_cache.set_guild(set_guild)

        r_1 = await create_mongo_cache.get_guild(2)
        assert isinstance(r_1, Guild)
        assert r_1 == set_guild

    @pytest.mark.asyncio
    async def test_delete_guild(self, create_mongo_cache):
        await create_mongo_cache.get_guild(1)

        await create_mongo_cache.delete_guild(1)

        with pytest.raises(GuildNotFound):
            await create_mongo_cache.get_guild(1)

    @pytest.mark.asyncio
    async def test_get_member(self, create_mongo_cache):
        """Tests members are fetched and converted correct"""
        with pytest.raises(MemberNotFound):
            await create_mongo_cache.get_member(1, 2)

        with pytest.raises(MemberNotFound):
            await create_mongo_cache.get_member(3, 1)

        r_1 = await create_mongo_cache.get_member(1, 1)
        assert isinstance(r_1, Member)
        assert len(r_1.messages) == 3
        assert isinstance(r_1.messages[0], Message)
        assert r_1.kick_count == 1
        assert r_1.warn_count == 2

        r_2 = await create_mongo_cache.get_member(2, 1)
        assert isinstance(r_2, Member)
        assert len(r_2.messages) == 0

    @pytest.mark.asyncio
    async def test_set_member(self, create_mongo_cache):
        """Tests set member with an existing guild"""
        with pytest.raises(MemberNotFound):
            await create_mongo_cache.get_member(3, 1)

        await create_mongo_cache.set_member(
            Member(
                3,
                1,
                messages=[
                    Message(1, 1, 1, 1, "Hello world"),
                    Message(2, 1, 1, 1, "foo bar"),
                ],
            )
        )

        r_1 = await create_mongo_cache.get_member(3, 1)
        assert isinstance(r_1, Member)
        assert len(r_1.messages) == 2
        assert r_1.messages[0].content == "Hello world"

    @pytest.mark.asyncio
    async def test_set_member_no_guild(self, create_mongo_cache):
        """Tests set member with no existing cached guild"""
        with pytest.raises(MemberNotFound):
            await create_mongo_cache.get_member(2, 2)

        with pytest.raises(GuildNotFound):
            await create_mongo_cache.get_guild(2)

        await create_mongo_cache.set_member(
            Member(2, 2, messages=[Message(1, 1, 1, 1, "Hello world")])
        )

        r_1 = await create_mongo_cache.get_guild(2)
        assert isinstance(r_1, Guild)
        assert len(r_1.members) == 1

        r_2 = await create_mongo_cache.get_member(2, 2)
        assert isinstance(r_2, Member)
        assert len(r_2.messages) == 1
        assert r_2.messages[0].content == "Hello world"

    @pytest.mark.asyncio
    async def test_delete_member(self, create_mongo_cache):
        await create_mongo_cache.get_member(1, 1)

        await create_mongo_cache.delete_member(1, 1)

        with pytest.raises(MemberNotFound):
            await create_mongo_cache.get_member(1, 1)

    @pytest.mark.asyncio
    async def test_add_message(self, create_mongo_cache):
        r_1 = await create_mongo_cache.get_member(1, 1)
        assert isinstance(r_1, Member)
        assert len(r_1.messages) == 3

        msg = Message(4, 1, 1, 1, "Hello world")
        await create_mongo_cache.add_message(msg)

        r_2 = await create_mongo_cache.get_member(1, 1)
        assert isinstance(r_2, Member)
        assert len(r_2.messages) == 4
        assert r_2.messages[3].content == "Hello world"

    @pytest.mark.asyncio
    async def test_add_message_no_exist(self, create_mongo_cache):
        """Tests add_message when the member doesnt exist"""
        with pytest.raises(MemberNotFound):
            await create_mongo_cache.get_member(3, 3)

        with pytest.raises(GuildNotFound):
            await create_mongo_cache.get_guild(3)

        await create_mongo_cache.add_message(Message(1, 1, 3, 3, "Foo bar"))

        r_1 = await create_mongo_cache.get_member(3, 3)
        assert isinstance(r_1, Member)
        assert len(r_1.messages) == 1

        assert r_1.messages[0].content == "Foo bar"

        r_2 = await create_mongo_cache.get_guild(3)
        assert isinstance(r_2, Guild)
        assert r_1 in list(r_2.members.values())

    @pytest.mark.asyncio
    async def test_reset_non_existent_member_count(self, create_mongo_cache):
        # Doesnt exist
        r_1 = await create_mongo_cache.reset_member_count(1, 3, ResetType.KICK_COUNTER)
        assert r_1 is None

    @pytest.mark.asyncio
    async def test_reset_kick_count(self, create_mongo_cache):
        r_1 = await create_mongo_cache.get_member(1, 1)
        assert isinstance(r_1, Member)
        assert r_1.kick_count == 1

        await create_mongo_cache.reset_member_count(1, 1, ResetType.KICK_COUNTER)

        r_2 = await create_mongo_cache.get_member(1, 1)
        assert isinstance(r_2, Member)
        assert r_2.kick_count == 0

    @pytest.mark.asyncio
    async def test_reset_warn_counter(self, create_mongo_cache):
        r_1 = await create_mongo_cache.get_member(1, 1)
        assert isinstance(r_1, Member)
        assert r_1.warn_count == 2

        await create_mongo_cache.reset_member_count(1, 1, ResetType.WARN_COUNTER)

        r_2 = await create_mongo_cache.get_member(1, 1)
        assert isinstance(r_2, Member)
        assert r_2.warn_count == 0

    @pytest.mark.asyncio
    async def test_get_all_members(self, create_mongo_cache):
        counter = 0
        async for member in create_mongo_cache.get_all_members(1):
            counter += 1
            assert isinstance(member, Member)

        assert counter == 2

    @pytest.mark.asyncio
    async def test_get_all_guilds(self, create_mongo_cache):
        counter = 0
        async for g in create_mongo_cache.get_all_guilds():
            counter += 1
            assert isinstance(g, Guild)

        assert counter == 1

    @pytest.mark.asyncio
    async def test_set_guild_is_idempotent(self, create_mongo_cache):
        await create_mongo_cache.delete_member(1, 2)
        await create_mongo_cache.set_guild(Guild(2))
        await create_mongo_cache.delete_member(1, 2)

        guild = await create_mongo_cache.get_guild(2)
        guild.members[1] = Member(1, 2)
        await create_mongo_cache.set_guild(guild)
        assert len(guild.members) == 1

    @pytest.mark.asyncio
    async def test_set_member_is_idempotent(self, create_mongo_cache):
        member = Member(
            3,
            1,
            messages=[
                Message(1, 1, 1, 1, "Hello world"),
                Message(2, 1, 1, 1, "foo bar"),
            ],
        )
        assert isinstance(member.messages[0].creation_time, datetime.datetime)
        await create_mongo_cache.set_member(member)
        assert isinstance(member.messages[0].creation_time, datetime.datetime)
