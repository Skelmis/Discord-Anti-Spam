import datetime
from unittest import mock
from unittest.mock import AsyncMock, patch

import pytest

from antispam import CorePayload, MemberNotFound, MemberAddonNotFound
from examples.custom_multistage_punishments.AntiSpamTrackerSubclass import (
    MyCustomTracker,
)
from tests.mocks import MockedMessage


class TestTrackerExampleSubclass:
    @pytest.mark.asyncio
    async def test_update_cache_no_update(self, create_example_tracker_subclass):
        """Appease coverage"""
        message = MockedMessage(guild_id=1, author_id=1).to_mock()
        data = CorePayload()
        await create_example_tracker_subclass.update_cache(message, data)

    @pytest.mark.asyncio
    async def test_update_cache(self, create_example_tracker_subclass: MyCustomTracker):
        message = MockedMessage(guild_id=1, author_id=1).to_mock()
        data = CorePayload(member_should_be_punished_this_message=True)

        await create_example_tracker_subclass.update_cache(message, data)

        values = await create_example_tracker_subclass.member_tracking.get_member_data(
            1, 1
        )
        assert isinstance(values, dict)
        assert "timestamps" in values
        assert len(values["timestamps"]) == 1

        message = MockedMessage(message_id=2, author_id=1, guild_id=1).to_mock()
        await create_example_tracker_subclass.update_cache(message, data)

        values = await create_example_tracker_subclass.member_tracking.get_member_data(
            1, 1
        )
        assert isinstance(values, dict)
        assert "timestamps" in values
        assert len(values["timestamps"]) == 2

    @pytest.mark.asyncio
    async def test_get_user_has_been_muted(self, create_example_tracker_subclass):
        with pytest.raises(MemberNotFound):
            await create_example_tracker_subclass.get_member_has_been_muted(
                MockedMessage().to_mock()
            )

        await create_example_tracker_subclass.member_tracking.set_member_data(
            1, 1, {"timestamps": [], "has_been_muted": True}
        )
        await create_example_tracker_subclass.member_tracking.set_member_data(
            2, 1, {"timestamps": [], "has_been_muted": False}
        )

        r_1 = await create_example_tracker_subclass.get_member_has_been_muted(
            MockedMessage(author_id=1, guild_id=1).to_mock()
        )
        assert r_1 is True

        r_2 = await create_example_tracker_subclass.get_member_has_been_muted(
            MockedMessage(author_id=2, guild_id=1).to_mock()
        )
        assert r_2 is False

    @pytest.mark.asyncio
    async def test_get_user_count(self, create_example_tracker_subclass):
        with pytest.raises(TypeError):
            await create_example_tracker_subclass.get_member_count(dict())

        with pytest.raises(TypeError):
            await create_example_tracker_subclass.get_member_count(set())

        with pytest.raises(TypeError):
            await create_example_tracker_subclass.get_member_count([1, 2, 3])

        with pytest.raises(MemberNotFound):
            await create_example_tracker_subclass.get_member_count(
                MockedMessage(is_in_guild=False).to_mock()
            )

        with pytest.raises(MemberNotFound):
            await create_example_tracker_subclass.get_member_count(
                MockedMessage(guild_id=1).to_mock()
            )

        # Actual tests which *should* work
        await create_example_tracker_subclass.member_tracking.set_member_data(
            1,
            1,
            {
                "timestamps": [
                    datetime.datetime.now(datetime.timezone.utc),
                ],
                "has_been_muted": True,
            },
        )
        r_1 = await create_example_tracker_subclass.get_member_count(
            MockedMessage(author_id=1, guild_id=1).to_mock()
        )
        assert r_1 == 1

    @pytest.mark.asyncio
    async def test_remove_timestamps(self, create_example_tracker_subclass):
        outdated_time = datetime.datetime.now(datetime.timezone.utc)
        outdated_time = outdated_time - datetime.timedelta(hours=1)

        await create_example_tracker_subclass.member_tracking.set_member_data(
            1,
            1,
            {
                "timestamps": [
                    outdated_time,
                    datetime.datetime.now(datetime.timezone.utc),
                ],
                "has_been_muted": False,
            },
        )

        await create_example_tracker_subclass.remove_outdated_timestamps(
            [
                outdated_time,
                datetime.datetime.now(datetime.timezone.utc),
            ],
            1,
            1,
        )

        r_1 = await create_example_tracker_subclass.member_tracking.get_member_data(
            1, 1
        )
        assert len(r_1["timestamps"]) == 1

    @pytest.mark.asyncio
    async def test_clean_cache(self, create_example_tracker_subclass):
        outdated_time = datetime.datetime.now(datetime.timezone.utc)
        outdated_time = outdated_time - datetime.timedelta(hours=1)
        await create_example_tracker_subclass.member_tracking.set_member_data(
            1,
            1,
            {
                "timestamps": [
                    outdated_time,
                    datetime.datetime.now(datetime.timezone.utc),
                ],
                "has_been_muted": False,
            },
        )
        await create_example_tracker_subclass.member_tracking.set_member_data(
            2,
            1,
            {
                "timestamps": [
                    outdated_time,
                ],
                "has_been_muted": False,
            },
        )
        await create_example_tracker_subclass.member_tracking.set_member_data(
            3,
            1,
            {
                "timestamps": [
                    outdated_time,
                ],
                "has_been_muted": True,
            },
        )
        await create_example_tracker_subclass.clean_cache()

        with pytest.raises(MemberAddonNotFound):
            await create_example_tracker_subclass.member_tracking.get_member_data(2, 1)

        r_1 = await create_example_tracker_subclass.member_tracking.get_member_data(
            1, 1
        )
        assert isinstance(r_1, dict)
        assert len(r_1["timestamps"]) == 1

        r_2 = await create_example_tracker_subclass.member_tracking.get_member_data(
            3, 1
        )
        assert isinstance(r_2, dict)
        assert len(r_2["timestamps"]) == 0

    @pytest.mark.asyncio
    async def test_do_punishment_kick(self, create_example_tracker_subclass):
        bot_msg = MockedMessage(author_id=98987).to_mock()
        # Should hit first return
        await create_example_tracker_subclass.do_punishment(bot_msg)

        # Should hit first except
        await create_example_tracker_subclass.do_punishment(MockedMessage().to_mock())

        # Stop appeasing coverage and start actually testing shit
        await create_example_tracker_subclass.member_tracking.set_member_data(
            1,
            1,
            {
                "timestamps": [
                    datetime.datetime.now(datetime.timezone.utc),
                ],
                "has_been_muted": True,
            },
        )

        msg_1 = MockedMessage(author_id=1, guild_id=1).to_mock()
        msg_1.guild.kick = kick_meth = AsyncMock()
        msg_1.channel.send = channel_sender = AsyncMock()

        assert channel_sender.call_count == 0
        with mock.patch("asyncio.sleep", new_callable=AsyncMock):
            await create_example_tracker_subclass.do_punishment(msg_1)

        assert channel_sender.call_count == 1
        assert kick_meth.call_count == 1

    @pytest.mark.asyncio
    async def test_do_punishment_warn(self, create_example_tracker_subclass):
        await create_example_tracker_subclass.member_tracking.set_member_data(
            1,
            1,
            {
                "timestamps": [
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                ],
                "has_been_muted": False,
            },
        )

        msg_1 = MockedMessage(author_id=1, guild_id=1).to_mock()
        msg_1.guild.kick = kick_meth = AsyncMock()
        msg_1.channel.send = channel_sender = AsyncMock()
        msg_1.author.add_roles = add_roles = AsyncMock()

        assert channel_sender.call_count == 0
        with mock.patch("asyncio.sleep", new_callable=AsyncMock):
            await create_example_tracker_subclass.do_punishment(msg_1)

        assert channel_sender.call_count == 2
        assert kick_meth.call_count == 0
        assert add_roles.call_count == 1
