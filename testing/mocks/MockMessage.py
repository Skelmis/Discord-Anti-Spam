"""
This 'mocks' a discord.Message so we can use it for testing
"""
import datetime
from unittest.mock import AsyncMock

from testing.mocks.MockGuild import MockedGuild
from testing.mocks.MockMember import get_mocked_member, get_mocked_bot
from testing.mocks.MockChannel import MockedChannel


def get_mocked_message(
    *,
    is_in_guild=True,
    member_kwargs=None,
    guild_kwargs=None,
    message_id=None,
    message_content=None
):
    """
    Return a mocked, usable message object
    """
    mock_message = AsyncMock(name="Message Mock")
    if member_kwargs:
        if member_kwargs.get("bot") is True:
            mem_id = member_kwargs.get("id")
            mem_id = 98987 if not mem_id and mem_id != 0 else mem_id
            mock_message.author = get_mocked_member(
                name=member_kwargs.get("name", "Mocked Bot"), id=mem_id, bot=True,
            )
        else:
            mem_id = member_kwargs.get("id")
            mem_id = 12345 if not mem_id and mem_id != 0 else mem_id
            mock_message.author = get_mocked_member(
                name=member_kwargs.get("name", "Skelmis"), id=mem_id,
            )
    else:
        mock_message.author = get_mocked_member(name="Skelmis", id=12345)
    mock_message.bot = False

    if is_in_guild:
        if guild_kwargs:
            mock_message.guild = MockedGuild(
                name=guild_kwargs.get("name", "Guild"),
                guild_id=guild_kwargs.get("id", 123456789),
            ).to_mock()
        else:
            mock_message.guild = MockedGuild(name="Guild").to_mock()
    else:
        mock_message.guild = None

    mock_message.channel = MockedChannel().to_mock()

    mock_message.created_at = datetime.datetime.now()

    mock_message.id = message_id or 12341234
    mock_message.clean_content = message_content or "This is the clean message content"
    mock_message.content = message_content or "This is the message content"

    return mock_message
