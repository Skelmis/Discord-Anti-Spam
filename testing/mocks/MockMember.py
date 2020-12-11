"""
This 'mocks' a discord.Member so we can use it for testing
"""
from unittest.mock import MagicMock

from testing.mocks.MockRole import get_mocked_role


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

    mock.roles = [get_mocked_role(), get_mocked_role(name="test role 2", id=252525)]

    return mock
