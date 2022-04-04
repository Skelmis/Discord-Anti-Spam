import datetime

import pytest

from antispam import MemberNotFound, Options, PluginCache
from antispam.dataclasses import CorePayload, Guild, Member
from antispam.plugins import AntiSpamTracker
from .conftest import MockClass

from .mocks import MockedMessage


class TestAntiSpamTracker:
    @pytest.mark.asyncio
    async def test_do_punishment(self, create_anti_spam_tracker):
        """Just for coverage"""
        await create_anti_spam_tracker.do_punishment(None)

    def test_init_raises(self, create_handler):
        with pytest.raises(ValueError):
            AntiSpamTracker(create_handler, None)

        with pytest.raises(TypeError):
            AntiSpamTracker(None, 1)

        with pytest.raises(TypeError):
            AntiSpamTracker(MockClass, 1)

        with pytest.raises(ValueError):
            AntiSpamTracker(create_handler, 1, valid_timestamp_interval="lol")

        with pytest.raises(TypeError):
            AntiSpamTracker(create_handler, 1, valid_timestamp_interval=MockClass)

    def test_init(self, create_handler):
        create_handler.options.no_punish = True  # Code coverage
        AntiSpamTracker(create_handler, 1)
        create_handler.options.no_punish = False
        AntiSpamTracker(create_handler, 1, valid_timestamp_interval=1)
        AntiSpamTracker(create_handler, 1, valid_timestamp_interval=1.0)

        tracker = AntiSpamTracker(create_handler, 5, 15)
        assert tracker.valid_global_interval == 15
        assert tracker.punish_min_amount == 5
        assert isinstance(tracker.member_tracking, PluginCache)

    @pytest.mark.asyncio
    async def test_propagate(self, create_anti_spam_tracker):
        """Tests this propagates the call to update_cache"""
        return_value = await create_anti_spam_tracker.propagate(
            MockedMessage().to_mock(), CorePayload()
        )
        assert return_value == {"status": "Cache updated"}

    @pytest.mark.asyncio
    async def test_update_cache_raises(self, create_anti_spam_tracker):
        with pytest.raises(TypeError):
            await create_anti_spam_tracker.update_cache(None, None)

        with pytest.raises(TypeError):
            await create_anti_spam_tracker.update_cache(
                MockedMessage().to_mock(), list()
            )

        with pytest.raises(TypeError):
            await create_anti_spam_tracker.update_cache(
                MockedMessage().to_mock(), set()
            )

        await create_anti_spam_tracker.update_cache(
            MockedMessage(is_in_guild=False).to_mock(), CorePayload()
        )
        await create_anti_spam_tracker.update_cache(
            MockedMessage().to_mock(), CorePayload()
        )

    @pytest.mark.asyncio
    async def test_update_cache(self, create_anti_spam_tracker):
        message = MockedMessage(guild_id=1, author_id=1).to_mock()

        # All we need to mock for this
        data = CorePayload(member_should_be_punished_this_message=True)

        await create_anti_spam_tracker.update_cache(message, data)

        values = await create_anti_spam_tracker.member_tracking.get_member_data(1, 1)
        assert len(values) == 1

        message = MockedMessage(message_id=2, author_id=1, guild_id=1).to_mock()
        await create_anti_spam_tracker.update_cache(message, data)

        values = await create_anti_spam_tracker.member_tracking.get_member_data(1, 1)
        assert len(values) == 2

    @pytest.mark.asyncio
    async def test_update_cache_addon_not_found(self, create_anti_spam_tracker):
        """For coverage"""
        await create_anti_spam_tracker.anti_spam_handler.cache.set_member(Member(1, 1))

        data = CorePayload(member_should_be_punished_this_message=True)

        await create_anti_spam_tracker.update_cache(
            MockedMessage(author_id=1, guild_id=1).to_mock(), data
        )

        values = await create_anti_spam_tracker.member_tracking.get_member_data(1, 1)
        assert len(values) == 1

    @pytest.mark.asyncio
    async def test_get_user_count(self, create_anti_spam_tracker):
        data = CorePayload(member_should_be_punished_this_message=True)
        await create_anti_spam_tracker.update_cache(
            MockedMessage(author_id=1, guild_id=1).to_mock(), data
        )
        values = await create_anti_spam_tracker.member_tracking.get_member_data(1, 1)
        assert len(values) == 1

        result = await create_anti_spam_tracker.get_member_count(
            MockedMessage(author_id=1, guild_id=1).to_mock()
        )
        assert result == 1

    @pytest.mark.asyncio
    async def test_get_user_count_raises(self, create_anti_spam_tracker):
        # TODO Uncomment #68
        # with pytest.raises(TypeError):
        #   await create_anti_spam_tracker.get_user_count(None)

        with pytest.raises(MemberNotFound):
            await create_anti_spam_tracker.get_member_count(
                MockedMessage(is_in_guild=False).to_mock()
            )

    @pytest.mark.asyncio
    async def test_remove_outdated_timestamps(self, create_anti_spam_tracker):
        timestamps = [
            datetime.datetime.now(tz=datetime.timezone.utc)
            - datetime.timedelta(seconds=45),
            datetime.datetime.now(tz=datetime.timezone.utc),
        ]
        assert len(timestamps) == 2

        await create_anti_spam_tracker.remove_outdated_timestamps(timestamps, 1, 1)

        result = await create_anti_spam_tracker.member_tracking.get_member_data(1, 1)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_remove_punishment(self, create_anti_spam_tracker):
        # TODO Uncomment #68
        # with pytest.raises(TypeError):
        #    await create_anti_spam_tracker.remove_punishments(MockClass)

        # Skip non guild messages
        await create_anti_spam_tracker.remove_punishments(
            MockedMessage(is_in_guild=False).to_mock()
        )

        # Return since guild wasnt found
        await create_anti_spam_tracker.remove_punishments(
            MockedMessage(author_id=1, guild_id=1).to_mock()
        )

        await create_anti_spam_tracker.anti_spam_handler.cache.set_member(Member(1, 1))
        await create_anti_spam_tracker.update_cache(
            MockedMessage(author_id=1, guild_id=1).to_mock(),
            CorePayload(member_should_be_punished_this_message=True),
        )

        result = await create_anti_spam_tracker.member_tracking.get_member_data(1, 1)
        assert len(result) == 1

        await create_anti_spam_tracker.remove_punishments(
            MockedMessage(author_id=1, guild_id=1).to_mock()
        )

        result = await create_anti_spam_tracker.member_tracking.get_member_data(1, 1)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_set_get_guild_valid_interval(self, create_anti_spam_tracker):
        await create_anti_spam_tracker.anti_spam_handler.cache.set_guild(
            Guild(1, Options())
        )

        result = await create_anti_spam_tracker.anti_spam_handler.cache.get_guild(1)
        assert len(result.addons) == 0

        await create_anti_spam_tracker._set_guild_valid_interval(1, 15)
        result = await create_anti_spam_tracker.anti_spam_handler.cache.get_guild(1)
        assert len(result.addons) == 1

        get_result = await create_anti_spam_tracker._get_guild_valid_interval(1)
        assert get_result == 15

        # Code coverage to ensure it works within try
        await create_anti_spam_tracker._set_guild_valid_interval(1, 25)
        result = await create_anti_spam_tracker.anti_spam_handler.cache.get_guild(1)
        assert len(result.addons) == 1

        get_result = await create_anti_spam_tracker._get_guild_valid_interval(1)
        assert get_result == 25

    @pytest.mark.asyncio
    async def test_set_guild_interval_without_guild(self, create_anti_spam_tracker):
        await create_anti_spam_tracker._set_guild_valid_interval(1, 15)
        result = await create_anti_spam_tracker.anti_spam_handler.cache.get_guild(1)
        assert len(result.addons) == 1

    @pytest.mark.asyncio
    async def test_get_guild_interval(self, create_anti_spam_tracker):
        result_one = await create_anti_spam_tracker._get_guild_valid_interval(1)
        assert result_one == 30000

        await create_anti_spam_tracker.anti_spam_handler.cache.set_guild(
            Guild(1, Options())
        )

        # Test where guild exists, just not within plugin
        result_two = await create_anti_spam_tracker._get_guild_valid_interval(1)
        assert result_two == 30000

        await create_anti_spam_tracker._set_guild_valid_interval(1, 15)
        result_three = await create_anti_spam_tracker._get_guild_valid_interval(1)
        assert result_three == 15

    @pytest.mark.asyncio
    async def test_get_guild_interval_check(self, create_anti_spam_tracker):
        await create_anti_spam_tracker.member_tracking.set_guild_data(
            1, addon_data={"test": []}
        )

        result_one = await create_anti_spam_tracker._get_guild_valid_interval(1)
        assert result_one == 30000

    @pytest.mark.asyncio
    async def test_is_spamming(self, create_anti_spam_tracker):
        # Test not in guild returns
        await create_anti_spam_tracker.is_spamming(
            MockedMessage(is_in_guild=False).to_mock()
        )

        result_one = await create_anti_spam_tracker.is_spamming(
            MockedMessage().to_mock()
        )
        assert result_one is False

        data = CorePayload(member_should_be_punished_this_message=True)
        await create_anti_spam_tracker.update_cache(
            MockedMessage(message_id=1).to_mock(), data
        )
        await create_anti_spam_tracker.update_cache(
            MockedMessage(message_id=2).to_mock(), data
        )

        result_two = await create_anti_spam_tracker.is_spamming(
            MockedMessage().to_mock()
        )
        assert result_two is False

        await create_anti_spam_tracker.update_cache(
            MockedMessage(message_id=3).to_mock(), data
        )
        result_three = await create_anti_spam_tracker.is_spamming(
            MockedMessage().to_mock()
        )
        assert result_three is True
