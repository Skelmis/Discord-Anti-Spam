import datetime

import pytest

from discord.ext.antispam.dataclasses import Guild, Member, CorePayload, Message

from discord.ext.antispam import Options
from .fixtures import create_bot, create_handler, create_memory_cache, create_core
from .mocks import MockedMessage


class TestCore:
    """A class devoted to testing core.py"""

    @pytest.mark.asyncio
    async def test_user_propagate_skip_guild(self, create_core):
        """Tests if the member gets skipped if not 'in guild'"""
        msg = MockedMessage(author_id=1, guild_id=1).to_mock()
        guild = Guild(1, Options)
        guild.members[1] = Member(1, 1, in_guild=False)

        payload = await create_core.propagate(msg, guild)

        assert payload == CorePayload(
            member_status="Bypassing message check since the member isn't seen to be in a guild"
        )

    @pytest.mark.asyncio
    async def test_clean_up(self, create_core):
        member = Member(1, 1)
        messages = [
            Message(
                1,
                1,
                1,
                1,
                "First message",
                datetime.datetime.now() - datetime.timedelta(minutes=1),
            ),
            Message(
                2,
                1,
                1,
                1,
                "Second message",
                datetime.datetime.now() - datetime.timedelta(minutes=1),
            ),
            Message(
                3,
                1,
                1,
                1,
                "Third message",
                datetime.datetime.now() - datetime.timedelta(minutes=1),
            ),
            Message(4, 1, 1, 1, "Fourth message", datetime.datetime.now()),
        ]
        member.messages = messages

        assert len(member.messages) == 4

        await create_core.clean_up(member, datetime.datetime.now(), 1)

        assert len(member.messages) == 1

    @pytest.mark.asyncio
    async def test_clean_up_duplicate_count(self, create_core):
        member = Member(1, 1)
        messages = [
            Message(
                1,
                1,
                1,
                1,
                "First message",
                datetime.datetime.now() - datetime.timedelta(minutes=1),
            ),
            Message(
                2,
                1,
                1,
                1,
                "Second message",
                datetime.datetime.now() - datetime.timedelta(minutes=1),
            ),
            Message(
                3,
                1,
                1,
                1,
                "Third message",
                datetime.datetime.now() - datetime.timedelta(minutes=1),
                is_duplicate=True,
            ),
            Message(4, 1, 1, 1, "Fourth message", datetime.datetime.now()),
        ]
        member.messages = messages
        member.duplicate_counter = 1

        await create_core.clean_up(member, datetime.datetime.now(), 1)

        assert member.duplicate_counter == 0

    def test_remove_duplicate_count(self, create_core):
        member = Member(1, 1)
        member.duplicate_counter = 5
        member.duplicate_channel_counter_dict = {15: 2}

        assert member.duplicate_counter == 5
        assert member.duplicate_channel_counter_dict == {15: 2}

        create_core._remove_duplicate_count(member, 1)
        assert member.duplicate_counter == 4
        assert member.duplicate_channel_counter_dict == {15: 2}

        create_core._remove_duplicate_count(member, 1, 2)
        assert member.duplicate_counter == 2
        assert member.duplicate_channel_counter_dict == {15: 2}

        create_core.options = Options(per_channel_spam=True)

        create_core._remove_duplicate_count(member, 15)
        assert member.duplicate_counter == 2
        assert member.duplicate_channel_counter_dict == {15: 1}

        create_core._remove_duplicate_count(member, 1)
        assert member.duplicate_counter == 2
        assert member.duplicate_channel_counter_dict == {15: 1}
