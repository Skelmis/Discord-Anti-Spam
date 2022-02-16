"""
This 'mocks' a discord.Message so we can use it for testing
"""
import datetime
from unittest.mock import AsyncMock, MagicMock

import discord

from .mock_channel import MockedChannel
from .mocked_guild import MockedGuild
from .mocked_member import MockedMember


class MockedMessage:
    def __init__(
        self,
        *,
        message_id=12341234,
        message_content="This is the message content",
        message_clean_content="This is the clean message content",
        author_name="Skelmis",
        author_id=12345,
        author_is_bot=False,
        is_in_guild=True,
        guild_name="Guild",
        guild_id=123456789,
        message_mentions=None,
    ):
        self.author = {"name": author_name, "id": author_id, "is_bot": author_is_bot}
        if author_is_bot:
            # Backwards compat
            self.author["name"] = (
                "Mocked Bot" if author_name == "Skelmis" else author_name
            )
            self.author["id"] = 98987 if author_id == 12345 else author_id

        self.is_in_guild = is_in_guild
        self.guild = {"name": guild_name, "id": guild_id}

        # Message related things
        self.message_id = message_id
        self.content = message_content
        self.clean_content = message_clean_content

        self.message_mentions = message_mentions or list()

    def to_mock(self):
        """Returns an AsyncMock matching the spec for this class"""
        # we still have to set stuff manually but changing values is nicer
        mock = AsyncMock(name="Message Mock", spec=discord.Message)

        # Author section
        mock.author = MockedMember(
            name=self.author["name"],
            member_id=self.author["id"],
            is_bot=self.author["is_bot"],
        ).to_mock()

        # Guild options and 'is_in_guild' are mutually exclusive
        if not self.is_in_guild:
            mock.guild = None
        else:
            mock.guild = MockedGuild(
                name=self.guild["name"], guild_id=self.guild["id"]
            ).to_mock()

        mock.channel = MockedChannel().to_mock()
        mock.created_at = datetime.datetime.now()

        mock.id = self.message_id
        mock.content = self.content
        mock.clean_content = self.clean_content
        mock.mentions = self.message_mentions
        mock.stickers = []

        mock.is_system = MagicMock(return_value=False)

        return mock
