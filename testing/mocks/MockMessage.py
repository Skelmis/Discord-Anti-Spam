"""
This 'mocks' a discord.Message so we can use it for testing
"""
import datetime
from unittest.mock import MagicMock

from testing.mocks.MockGuild import get_mocked_guild
from testing.mocks.MockMember import get_mocked_member, get_mocked_bot
from testing.mocks.MockChannel import get_mocked_channel


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
    mock_message = MagicMock(name="Message Mock")
    if member_kwargs:
        if member_kwargs.get("bot") is True:
            mock_message.author = get_mocked_member(
                name=member_kwargs.get("name", "Mocked Bot"),
                id=member_kwargs.get("id", 98987),
                bot=True,
            )
        else:
            mock_message.author = get_mocked_member(
                name=member_kwargs.get("name", "Skelmis"),
                id=member_kwargs.get("id", 12345),
            )
    else:
        mock_message.author = get_mocked_member(name="Skelmis", id=12345)
    mock_message.bot = False

    if is_in_guild:
        if guild_kwargs:
            mock_message.guild = get_mocked_guild(
                name=guild_kwargs.get("name", "Guild"),
                id=guild_kwargs.get("id", 123456789),
            )
        else:
            mock_message.guild = get_mocked_guild(name="Guild")
    else:
        mock_message.guild = False

    mock_message.channel = get_mocked_channel()

    mock_message.created_at = datetime.datetime.now()

    mock_message.id = message_id or 12341234
    mock_message.clean_content = message_content or "This is the message content"

    return mock_message
