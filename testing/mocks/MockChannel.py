"""
This 'mocks' a discord.TextChannel so we can use it for testing
"""
from unittest.mock import AsyncMock

import discord

from testing.mocks.MockRole import get_mocked_role


class MockedChannel(AsyncMock):
    def __init__(self, name=None, channel_id=None):
        self.name = name or "Mocked Channel"
        self.id = int(channel_id) if channel_id else 98987
        self.mention = f"<@&{self.id}>"


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
