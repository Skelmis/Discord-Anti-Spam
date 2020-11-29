"""
This 'mocks' a discord.Member so we can use it for testing
"""
from unittest.mock import MagicMock


def get_mocked_member(*, name=None, id=None):
    """
    Return a mocked, usable message object
    """
    name = name or "Mocked Member"
    id = int(id) if id else 12345

    mock = MagicMock(name="Member Mock")
    mock.id = id
    mock.display_name = name
    mock.mention = f"<@{id}>"

    return mock
