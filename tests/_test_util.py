import datetime

import discord

from antispam import visualizer  # noqa
from antispam.util import (
    dict_to_embed,
    embed_to_string,
    get_aware_time,
    substitute_args,
    transform_message,
)
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

    def test_embed_skips_values(self):
        """Tests we skip the footer and author checks on some cases"""
        embed = discord.Embed()
        assert "" == embed_to_string(embed=embed)

        embed = discord.Embed(title="Hello", description="World")
        embed.set_footer(icon_url="This is weird")
        embed.set_author(name="test", url="Its almost as if")
        assert "Hello\nWorld\ntest\n" == embed_to_string(embed)

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

    def test_edge_dict_to_embed(self):
        """Tests edge cases for dict_to_embed"""
        data = {
            "author": {"icon_url": "$USERAVATAR", "name": "test"},
            "footer": {"icon_url": "$USERAVATAR"},
            "timestamp": True,
        }

        mock_message = MockedMessage().to_mock()

        test_embed = dict_to_embed(
            data, mock_message, {"warn_count": 1, "kick_count": 2}
        )

        user_footer = substitute_args(
            "$USERAVATAR", mock_message, {"warn_count": 1, "kick_count": 2}
        )

        embed = discord.Embed(timestamp=mock_message.created_at)
        embed.set_footer(icon_url=user_footer)
        embed.set_author(
            name="test",
            icon_url=user_footer,
        )

        assert embed.to_dict() == test_embed.to_dict()

    def test_further_edge_cases_for_to_dict(self):
        data = {
            "author": {"icon_url": "y", "name": "test"},
            "footer": {"icon_url": "x"},
            "timestamp": True,
        }

        mock_message = MockedMessage().to_mock()

        test_embed = dict_to_embed(
            data, mock_message, {"warn_count": 1, "kick_count": 2}
        )

        embed = discord.Embed(timestamp=mock_message.created_at)
        embed.set_footer(icon_url="x")
        embed.set_author(
            name="test",
            icon_url="y",
        )

        assert embed.to_dict() == test_embed.to_dict()

    def test_to_dict_colors(self):
        data = {"colour": 0xFFFFFF, "color": 0x000000}
        mock_message = MockedMessage().to_mock()
        data_embed = dict_to_embed(
            data, mock_message, {"warn_count": 1, "kick_count": 2}
        )
        embed = discord.Embed(color=0xFFFFFF)

        assert embed.to_dict() == data_embed.to_dict()

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
        assert datetime.datetime.now(datetime.timezone.utc).replace(
            microsecond=0
        ) == get_aware_time().replace(microsecond=0)
