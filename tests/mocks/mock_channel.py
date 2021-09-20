"""
This 'mocks' a discord.TextChannel so we can use it for testing
"""
from unittest.mock import AsyncMock

import discord


class MockedChannel:
    def __init__(self, name=None, channel_id=None):
        self.name = name or "Mocked Channel"
        self.id = int(channel_id) if channel_id else 98987
        self.mention = f"<@&{self.id}>"

    def to_mock(self):
        """Returns an AsyncMock matching the spec for this class"""
        # we still have to set stuff manually but changing values is nicer
        mock = AsyncMock(name="Channel Mock", spec=discord.TextChannel)

        mock.name = self.name
        mock.id = self.id
        mock.mention = f"<@&{self.id}>"

        mock.fetch_message = self.fetch_message

        return mock

    @staticmethod
    async def fetch_message(message_id):
        from tests.mocks import MockedMessage

        return MockedMessage(message_id=message_id).to_mock()
