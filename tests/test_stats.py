import pytest

from antispam.dataclasses import CorePayload
from antispam.plugins import Stats  # noqa


from .mocks import MockedMessage


class TestStats:
    def test_init(self, create_handler):
        s = Stats(create_handler)
        assert s.data == {
            "pre_invoke_calls": {},
            "after_invoke_calls": {},
            "propagate_calls": 0,
            "guilds": {},
            "members": {},
        }
        assert s.is_pre_invoke is False

    @pytest.mark.asyncio()
    async def test_stats_creates(self, create_stats):
        """Tests the plugin creates stats entries where required"""
        create_stats.handler.pre_invoke_plugins["before"] = True
        create_stats.handler.after_invoke_plugins["after"] = True

        assert create_stats.data == {
            "pre_invoke_calls": {},
            "after_invoke_calls": {},
            "propagate_calls": 0,
            "guilds": {},
            "members": {},
        }

        await create_stats.propagate(
            MockedMessage().to_mock(),
            CorePayload(member_should_be_punished_this_message=True),
        )

        assert len(create_stats.data["pre_invoke_calls"]) == 1
        assert len(create_stats.data["after_invoke_calls"]) == 1
        assert len(create_stats.data["members"]) == 1
        assert len(create_stats.data["guilds"]) == 1
        assert create_stats.data["propagate_calls"] == 1

    @pytest.mark.asyncio()
    async def test_stats_adds(self, create_stats):
        """Tests the plugin adds to existing data"""
        create_stats.handler.pre_invoke_plugins["before"] = True
        create_stats.handler.after_invoke_plugins["after"] = True
        create_stats.data = {
            "pre_invoke_calls": {"before": {"calls": 1}},
            "after_invoke_calls": {"after": {"calls": 1}},
            "propagate_calls": 1,
            "guilds": {123456789: {"calls": 1, "total_messages_punished": 1}},
            "members": {12345: {"calls": 1, "times_punished": 1}},
        }

        await create_stats.propagate(
            MockedMessage().to_mock(),
            CorePayload(),
        )
        await create_stats.propagate(
            MockedMessage().to_mock(),
            CorePayload(member_should_be_punished_this_message=True),
        )

        assert create_stats.data == {
            "pre_invoke_calls": {"before": {"calls": 3}},
            "after_invoke_calls": {"after": {"calls": 3}},
            "propagate_calls": 3,
            "guilds": {123456789: {"calls": 3, "total_messages_punished": 2}},
            "members": {12345: {"calls": 3, "times_punished": 2}},
        }

    @pytest.mark.asyncio
    async def test_load_from_dict(self, create_handler):
        stats = await Stats.load_from_dict(create_handler, {"test": True})
        assert stats.data == {"test": True}

    @pytest.mark.asyncio
    async def test_save_from_dict(self, create_stats):
        create_stats.data = {
            "pre_invoke_calls": {"before": {"calls": 1}},
            "after_invoke_calls": {"after": {"calls": 1}},
            "propagate_calls": 1,
            "guilds": {123456789: {"calls": 1, "total_messages_punished": 1}},
            "members": {12345: {"calls": 1, "times_punished": 1}},
        }
        data = await create_stats.save_to_dict()
        assert data == {
            "pre_invoke_calls": {"before": {"calls": 1}},
            "after_invoke_calls": {"after": {"calls": 1}},
            "propagate_calls": 1,
            "guilds": {123456789: {"calls": 1, "total_messages_punished": 1}},
            "members": {12345: {"calls": 1, "times_punished": 1}},
        }
