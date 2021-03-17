"""
This 'mocks' a discord.Member so we can use it for testing
"""
import discord
from unittest.mock import AsyncMock

from discord.ext import commands

from testing.mocks.MockRole import MockedRole


class MockedMember:
    def __init__(self, name=None, member_id=None, is_bot=False):
        self.name = name or "Mocked Member"
        self.id = int(member_id) if member_id else 12345
        self.mention = f"<@{self.id}>"
        self.is_bot = is_bot

    def to_mock(self):
        """Returns an AsyncMock matching the spec for this class"""
        # we still have to set stuff manually but changing values is nicer
        mock = AsyncMock(name="Member Mock")

        mock.name = self.name
        mock.display_name = self.name
        mock.id = self.id
        mock.bot = self.is_bot

        mock.roles = [MockedRole().to_mock(), MockedRole(name="test role 2", role_id=252525).to_mock()]
        mock.top_role.position = 5
        # TODO Make ^ be conditional on the type of mock (Member, User, Bot)

        return mock

def get_mocked_member(*, name=None, id=None, bot=False):
    """
    Return a mocked, usable member object
    """
    name = name or "Mocked Member"
    id = int(id) if id or id == 0 else 12345

    mock = AsyncMock(name="Member Mock")
    mock.id = id
    mock.display_name = name
    mock.mention = f"<@{id}>"
    mock.bot = bot

    mock.roles = [MockedRole().to_mock(), MockedRole(name="test role 2", role_id=252525).to_mock()]
    mock.top_role.position = 5

    return mock


def get_mocked_user(*, name=None, id=None, bot=False):
    """
    Return a mocked, usable user object
    """
    name = name or "Mocked Member"
    id = int(id) if id else 12345

    mock = AsyncMock(name="Member Mock")
    mock.id = id
    mock.display_name = name
    mock.mention = f"<@{id}>"
    mock.bot = bot

    return mock


def get_mocked_bot(*, name=None, id=None):
    mock = AsyncMock(name="Bot Mock")
    name = name or "Mocked Bot"
    id = int(id) if id else 98987

    mock.user.name = name
    mock.user.id = id
    mock.user.mention = f"<@{id}>"
    mock.user.bot = True

    mock.user.roles = [
        MockedRole(),
        MockedRole(name="test role 2", role_id=252525).to_mock(),
    ]

    return mock
