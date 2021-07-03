"""
This 'mocks' a discord.Guild so we can use it for testing
"""
from unittest.mock import AsyncMock

import discord

from tests.mocks.mocked_member import MockedMember


class MockedGuild:
    def __init__(self, name=None, guild_id=None):
        self.name = name or "Mocked Guild"
        self.id = int(guild_id) if guild_id else 123456789
        self.mention = f"<@&{self.id}>"

    def to_mock(self):
        """Returns an AsyncMock matching the spec for this class"""
        # we still have to set stuff manually but changing values is nicer
        mock = AsyncMock(name="Guild Mock", spec=discord.Guild)

        mock.name = self.name
        mock.id = self.id

        mock.me = MockedMember(name="Bot", member_id=54321).to_mock()
        mock.me.top_role.position = 100  # Bot should have higher role by default

        return mock
