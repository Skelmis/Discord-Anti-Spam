"""
This 'mocks' a discord.TextChannel so we can use it for testing
"""
from unittest.mock import AsyncMock

import discord

from testing.mocks.MockRole import get_mocked_role


class MockedChannel:
    def __init__(self, name=None, channel_id=None):
        self.name = name or "Mocked Channel"
        self.id = int(channel_id) if channel_id else 98987
        self.mention = f"<@&{self.id}>"

    def to_mock(self):
        """Returns an AsyncMock matching the spec for this class"""
        mock = AsyncMock()
        for k, v in self.__dict__.items():
            print(k, v)
            mock[k] = v

        print(dir(mock))
        mock.id = self.id
        print(dir(mock))

        return mock


def get_mocked_channel(*, name=None, id=None):
    """
    Return a mocked, usable channel object
    """
    name = name or "Mocked Channel"
    id = int(id) if id else 98987

    mock = AsyncMock(name="Channel Mock", spec=discord.TextChannel)
    mock.id = id
    mock.name = name
    mock.mention = f"<@&{id}>"

    return mock


print(MockedChannel().to_mock().id)
print(get_mocked_channel().id)
