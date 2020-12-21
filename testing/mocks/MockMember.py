"""
This 'mocks' a discord.Member so we can use it for testing
"""
from unittest.mock import MagicMock

from testing.mocks.MockRole import get_mocked_role


def get_mocked_member(*, name=None, id=None, bot=False):
    """
    Return a mocked, usable message object
    """
    name = name or "Mocked Member"
    id = int(id) if id else 12345

    mock = MagicMock(name="Member Mock")
    mock.id = id
    mock.display_name = name
    mock.mention = f"<@{id}>"
    mock.bot = bot

    mock.roles = [get_mocked_role(), get_mocked_role(name="test role 2", id=252525)]

    return mock


def get_mocked_user(*, name=None, id=None, bot=False):
    """
    Return a mocked, usable message object
    """
    name = name or "Mocked Member"
    id = int(id) if id else 12345

    mock = MagicMock(name="Member Mock")
    mock.id = id
    mock.display_name = name
    mock.mention = f"<@{id}>"
    mock.bot = bot

    return mock


def get_mocked_bot(*, name=None, id=None):
    mock = MagicMock(name="Bot Mock")
    name = name or "Mocked Bot"
    id = int(id) if id else 98987

    mock.user.name = name
    mock.user.id = id
    mock.user.mention = f"<@{id}>"
    mock.user.bot = True

    mock.user.roles = [
        get_mocked_role(),
        get_mocked_role(name="test role 2", id=252525),
    ]

    return mock
