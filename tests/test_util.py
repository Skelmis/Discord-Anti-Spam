import datetime

import discord

# noinspection PyUnresolvedReferences
from discord.ext.antispam.util import (
    embed_to_string,
    dict_to_embed,
    transform_message,
    get_aware_time,
)

from discord.ext.antispam import visualizer  # noqa
from tests.mocks import MockedMessage


class TestUtil:
    def test_embed_to_string(self):
        embed = discord.Embed()
        assert "" == embed_to_string(embed=embed)

        embed = discord.Embed(title="Hello", description="World")
        embed.set_footer(text="This is weird")
        embed.set_author(name="Its almost as if")
        embed.add_field(name="I am", value="Alive")
        embed.add_field(name="That would be weird tho", value="Right?")
        assert (
            "Hello\nWorld\nThis is weird\nIts almost as if\nI am\nAlive\nThat would be weird tho\nRight?\n"
            == embed_to_string(embed)
        )

    def test_dict_to_embed(self):
        warn_embed_dict = {
            "title": "**Dear Dave**",
            "description": "You are being warned for spam, please stop!",
            "color": 0xFF0000,
            "footer": {"text": "BOT"},
            "author": {"name": "Guild"},
            "fields": [
                {"name": "Current warns:", "value": "1"},
                {"name": "Current kicks:", "value": "2", "inline": False},
            ],
        }

        mock_message = MockedMessage().to_mock()

        test_embed = dict_to_embed(
            warn_embed_dict, mock_message, {"warn_count": 1, "kick_count": 2}
        )

        embed = discord.Embed(
            title="**Dear Dave**",
            description="You are being warned for spam, please stop!",
            color=0xFF0000,
        )
        embed.set_footer(text="BOT")
        embed.set_author(name="Guild")
        embed.add_field(name="Current warns:", value="1")
        embed.add_field(name="Current kicks:", value="2", inline=False)

        assert embed.to_dict() == test_embed.to_dict()

    def test_transform_message(self):
        warn_embed_dict = {
            "title": "**Dear $USERNAME**",
            "description": "You are being warned for spam, please stop!",
            "color": 0xFF0000,
            "footer": {"text": "$BOTNAME"},
            "author": {"name": "$GUILDNAME"},
            "fields": [
                {"name": "Current warns:", "value": "$WARNCOUNT"},
                {"name": "Current kicks:", "value": "$KICKCOUNT", "inline": False},
            ],
        }

        mock_message = MockedMessage().to_mock()
        warn_dict = {"warn_count": 1, "kick_count": 2}

        test_embed = transform_message(warn_embed_dict, mock_message, warn_dict)

        embed = discord.Embed(
            title="**Dear Skelmis**",
            description="You are being warned for spam, please stop!",
            color=0xFF0000,
        )
        embed.set_footer(text="Bot")
        embed.set_author(name="Guild")
        embed.add_field(name="Current warns:", value="1")
        embed.add_field(name="Current kicks:", value="2", inline=False)

        assert embed.to_dict() == test_embed.to_dict()

        message = transform_message("Hello $MENTIONUSER", mock_message, warn_dict)
        assert "Hello <@12345>" == message

    def test_visualizer(self):
        message = visualizer(
            "Hello $MENTIONUSER",
            MockedMessage().to_mock(),
            {"warn_count": 1, "kick_count": 2},
        )
        assert "Hello <@12345>" == message

        warn_embed_dict = '{"title": "test"}'
        test_embed = visualizer(
            warn_embed_dict,
            MockedMessage().to_mock(),
            {"warn_count": 1, "kick_count": 2},
        )
        embed = discord.Embed(title="test")

        assert isinstance(test_embed, discord.Embed)
        assert embed.to_dict() == test_embed.to_dict()

    def test_get_aware_time(self):
        assert datetime.datetime.now(datetime.timezone.utc) == get_aware_time()
