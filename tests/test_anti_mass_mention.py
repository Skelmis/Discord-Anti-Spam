import datetime

import pytest

from antispam.plugins import AntiMassMention
from antispam.plugins.anti_mass_mention import MassMentionPunishment, Tracking
from antispam.util import get_aware_time

from .mocks import MockedMessage


class TestMassMention:
    def test_mass_mention_payload(self):
        test = MassMentionPunishment(1, 2, 3, True)
        assert test == MassMentionPunishment(1, 2, 3, True)

    def test_tracking(self):
        date = datetime.datetime.now()
        test = Tracking(1, date)
        assert test == Tracking(1, date)

    def test_anti_mass_mention_init_raises(self):
        with pytest.raises(ValueError):
            AntiMassMention(
                None,
                None,
                min_mentions_per_message=5,
                total_mentions_before_punishment=1,
            )

        with pytest.raises(ValueError):
            AntiMassMention(None, None, time_period=0)

        with pytest.raises(ValueError):
            AntiMassMention(None, None, time_period=-1)

    def test_anti_mass_mention_init(self, create_bot, create_handler):
        cls = AntiMassMention(
            create_bot,
            create_handler,
            total_mentions_before_punishment=15,
            time_period=25000,
            min_mentions_per_message=10,
        )
        assert cls.bot == create_bot
        assert cls.min_mentions_per_message == 10
        assert cls.time_period == 25000
        assert cls.total_mentions_before_punishment == 15

    @pytest.mark.asyncio
    async def test_clean_mention_timestamps(self, create_anti_mass_mention):
        await create_anti_mass_mention._clean_mention_timestamps(
            1, 1, datetime.datetime.now()
        )

        await create_anti_mass_mention.data.set_member_data(
            1,
            1,
            {
                "total_mentions": [
                    Tracking(
                        mentions=1,
                        timestamp=get_aware_time() - datetime.timedelta(seconds=45),
                    ),
                    Tracking(mentions=5, timestamp=get_aware_time()),
                ]
            },
        )

        result = await create_anti_mass_mention.data.get_member_data(1, 1)
        assert len(result["total_mentions"]) == 2

        await create_anti_mass_mention._clean_mention_timestamps(1, 1, get_aware_time())

        result = await create_anti_mass_mention.data.get_member_data(1, 1)
        assert len(result["total_mentions"]) == 1

    @pytest.mark.asyncio
    async def test_propagate(self, create_anti_mass_mention):
        message = MockedMessage(message_id=1).to_mock()
        return_value = await create_anti_mass_mention.propagate(message)

        assert return_value == {"action": "No action taken"}

    @pytest.mark.asyncio
    async def test_propagate_set(self, create_anti_mass_mention):
        """Tests the set ignores duplicate mentions"""
        message = MockedMessage(message_mentions=[1, 1, 1, 1, 1, 1]).to_mock()
        return_value = await create_anti_mass_mention.propagate(message)

        assert return_value == {"action": "No action taken"}

    @pytest.mark.asyncio
    async def test_propagate_non_overall(self, create_anti_mass_mention):
        message = MockedMessage(
            author_id=1, guild_id=1, message_mentions=[1, 2, 3, 4, 5, 6, 7, 8, 9]
        ).to_mock()
        return_value = await create_anti_mass_mention.propagate(message)

        assert return_value == MassMentionPunishment(
            member_id=1, guild_id=1, channel_id=98987, is_overall_punishment=False
        )

    @pytest.mark.asyncio
    async def test_propagate_is_overall(self, create_anti_mass_mention):
        message = MockedMessage(message_id=1, message_mentions=[1, 2, 3, 4]).to_mock()

        return_value = await create_anti_mass_mention.propagate(message)
        assert return_value == {"action": "No action taken"}

        # Again
        message = MockedMessage(message_id=2, message_mentions=[1, 2, 3, 4]).to_mock()
        return_value = await create_anti_mass_mention.propagate(message)
        assert return_value == {"action": "No action taken"}

        # We should now trip it
        message = MockedMessage(message_id=3, message_mentions=[1, 2, 3, 4]).to_mock()
        return_value = await create_anti_mass_mention.propagate(message)
        assert return_value == MassMentionPunishment(
            member_id=12345,
            guild_id=123456789,
            channel_id=98987,
            is_overall_punishment=True,
        )
