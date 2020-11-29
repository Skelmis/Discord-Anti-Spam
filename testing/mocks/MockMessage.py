"""
This 'mocks' a discord.Message so we can use it for testing
"""
import datetime
from unittest.mock import MagicMock

from testing.mocks.MockGuild import get_mocked_guild
from testing.mocks.MockMember import get_mocked_member


def get_mocked_message():
    """
    Return a mocked, usable message object
    """
    mock_message = MagicMock(name="Message Mock")
    mock_message.author = get_mocked_member(name="Skelmis", id=12345)

    mock_message.guild = get_mocked_guild(name="Guild")

    mock_message.created_at = datetime.datetime.now()

    return mock_message
