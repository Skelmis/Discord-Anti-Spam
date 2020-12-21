"""
This 'mocks' a discord.TextChannel so we can use it for testing
"""
from unittest.mock import MagicMock

from testing.mocks.MockRole import get_mocked_role


def get_mocked_channel(*, name=None, id=None):
    """
    Return a mocked, usable channel object
    """
    name = name or "Mocked Channel"
    id = int(id) if id else 98987

    mock = MagicMock(name="Channel Mock")
    mock.id = id
    mock.name = name
    mock.mention = f"<@&{id}>"

    return mock
