import datetime
from unittest.mock import AsyncMock

import discord
import pytest

from antispam.dataclasses import Guild, Member, CorePayload, Message

from antispam import Options, LogicError, MissingGuildPermissions, DuplicateObject
from .fixtures import (
    create_bot,
    create_handler,
    create_memory_cache,
    create_core,
    MockClass,
)
from .mocks import MockedMessage


# noinspection DuplicatedCode
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
    async def test_skip_per_channel_per_guild(self, create_core):
        create_core.options.is_per_channel_per_guild = False
        await create_core.cache.set_guild(Guild(1, Options()))
        await create_core.propagate(
            MockedMessage(guild_id=1).to_mock(), Guild(1, Options())
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

    def test_get_duplicate_count(self, create_core):
        member = Member(1, 1)
        member.duplicate_counter = 5
        member.duplicate_channel_counter_dict = {15: 2}

        assert create_core._get_duplicate_count(member, 1) == 5

        create_core.options = Options(per_channel_spam=True)

        assert create_core._get_duplicate_count(member) == 1
        assert create_core._get_duplicate_count(member, 5) == 1
        assert create_core._get_duplicate_count(member, 15) == 2

    def test_increment_duplicate_count(self, create_core):
        member = Member(1, 1)
        assert member.duplicate_counter == 1

        create_core._increment_duplicate_count(member, 1)
        assert member.duplicate_counter == 2

        create_core._increment_duplicate_count(member, 1, 3)
        assert member.duplicate_counter == 5

        create_core.options = Options(per_channel_spam=True)

        create_core._increment_duplicate_count(member, 1, 1)
        assert member.duplicate_channel_counter_dict == {1: 2}

    def test_calculate_ratios(self, create_core):
        member = Member(1, 1)
        member.messages = [Message(1, 1, 1, 1, "Hello world", datetime.datetime.now())]
        message = Message(2, 1, 1, 1, "Hello world", datetime.datetime.now())

        assert member.duplicate_counter == 1

        create_core._calculate_ratios(message, member)

        assert member.duplicate_counter == 2
        assert message.is_duplicate is True

    def test_calculate_ratios_per_channel(self, create_core):
        member = Member(1, 1)
        member.messages = [Message(1, 1, 1, 1, "Hello world", datetime.datetime.now())]
        message = Message(2, 2, 1, 1, "Hello world", datetime.datetime.now())
        create_core.options = Options(per_channel_spam=True)

        assert member.duplicate_counter == 1

        create_core._calculate_ratios(message, member)

        assert member.duplicate_counter == 1
        assert message.is_duplicate is False

    @pytest.mark.asyncio
    async def test_propagate_no_punish(self, create_core):
        await create_core.cache.set_guild(Guild(1, Options()))
        member = Member(1, 1)
        await create_core.cache.set_member(member)
        create_core._increment_duplicate_count(member, 1, 15)

        create_core.options.no_punish = True
        guild = await create_core.cache.get_guild(1)
        return_data = await create_core.propagate_user(
            MockedMessage(guild_id=1, author_id=1).to_mock(), guild
        )
        assert return_data == CorePayload(
            member_should_be_punished_this_message=True,
            member_status="Member should be punished, however, was not due to no_punish being True",
        )

    @pytest.mark.asyncio
    async def test_propagate_warn_only(self, create_core):
        member = Member(1, 1)
        await create_core.cache.set_member(member)
        create_core._increment_duplicate_count(member, 1, 15)
        guild = await create_core.cache.get_guild(1)

        create_core.options.warn_only = True
        return_data = await create_core.propagate_user(
            MockedMessage(guild_id=1, author_id=1).to_mock(), guild
        )
        assert return_data == CorePayload(
            member_should_be_punished_this_message=True,
            member_status="Member was warned",
            member_was_warned=True,
            member_warn_count=1,
            member_duplicate_count=15,
        )

        # Test embed coverage
        create_core.options.guild_warn_message = {"title": "test"}
        return_data = await create_core.propagate_user(
            MockedMessage(guild_id=1, author_id=1, message_id=2).to_mock(), guild
        )
        assert return_data == CorePayload(
            member_should_be_punished_this_message=True,
            member_status="Member was warned",
            member_was_warned=True,
            member_warn_count=2,
            member_duplicate_count=16,
        )

    @pytest.mark.asyncio
    async def test_propagate_kicks(self, create_core):
        member = Member(1, 1)
        member.warn_count = 3
        create_core._increment_duplicate_count(member, 1, 7)
        await create_core.cache.set_member(member)
        guild = await create_core.cache.get_guild(1)

        return_data = await create_core.propagate_user(
            MockedMessage(guild_id=1, author_id=1).to_mock(), guild
        )
        assert return_data == CorePayload(
            member_should_be_punished_this_message=True,
            member_status="Member was kicked",
            member_was_kicked=True,
            member_warn_count=3,
            member_kick_count=1,
            member_duplicate_count=7,
        )

    @pytest.mark.asyncio
    async def test_propagate_bans(self, create_core):
        member = Member(1, 1)
        member.warn_count = 3
        member.kick_count = 3
        create_core._increment_duplicate_count(member, 1, 7)
        await create_core.cache.set_member(member)
        guild = await create_core.cache.get_guild(1)

        return_data = await create_core.propagate_user(
            MockedMessage(guild_id=1, author_id=1).to_mock(), guild
        )
        assert return_data == CorePayload(
            member_should_be_punished_this_message=True,
            member_status="Member was banned",
            member_was_banned=True,
            member_warn_count=3,
            member_kick_count=4,
            member_duplicate_count=7,
        )

    def test_calculate_ratios_raises(self, create_core):
        member = Member(
            1, 1, messages=[Message(1, 2, 3, 4, "One"), Message(2, 2, 3, 4, "Two")]
        )

        with pytest.raises(DuplicateObject):
            create_core._calculate_ratios(Message(1, 2, 3, 4, "One"), member)

    def test_calculate_ratios_does_nothing(self, create_core):
        """Tests the loop does nothing on different messages"""
        member = Member(1, 1, messages=[Message(1, 2, 3, 4, "Hello I am the world")])

        create_core._calculate_ratios(Message(2, 2, 3, 4, "My name is Ethan!"), member)

    def test_increment_duplicate_existing(self, create_core):
        """Tests the count increments even when already existing"""
        member = Member(1, 1, duplicate_channel_counter_dict={5: 1})
        create_core.options.per_channel_spam = True
        create_core._increment_duplicate_count(member, 5)
        assert member.duplicate_channel_counter_dict[5] == 2
