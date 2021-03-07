"""
This 'mocks' a discord.Guild so we can use it for testing
"""
from unittest.mock import AsyncMock

import discord

from testing.mocks.MockMember import get_mocked_member


def get_mocked_guild(*, name=None, id=None):
    """
    Return a mocked, usable message object
    """
    name = name or "Mocked Guild"
    id = int(id) if id else 123456789

    mock = AsyncMock(name="Guild Mock", spec=discord.Guild)
    mock.id = id
    mock.name = name
    mock.mention = f"<@{id}>"

    mock.me = get_mocked_member(name="Bot", id=54321)
    mock.me.top_role.position = 100 # Bot should have higher role by default

    return mock
