"""
This 'mocks' a discord.Role so we can use it for testing
"""
from unittest.mock import AsyncMock

import discord


class MockedRole:
    def __init__(self, name=None, role_id=None):
        self.name = name or "Mocked Role"
        self.id = int(role_id) if role_id else 151515
        self.mention = f"<@&{self.id}>"

    def to_mock(self):
        """Returns an AsyncMock matching the spec for this class"""
        # we still have to set stuff manually but changing values is nicer
        mock = AsyncMock(name="Role Mock", spec=discord.Role)

        mock.name = self.name
        mock.id = self.id
        mock.mention = f"<@&{self.id}>"

        return mock
