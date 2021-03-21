"""
The MIT License (MIT)

Copyright (c) 2020 Skelmis

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import unittest

from AntiSpam.Util import *
from testing.mocks.MockMessage import MockedMessage


class TestUtil(unittest.TestCase):
    """
    Used to test the util functions
    """

    def test_embedToString(self):
        embed = discord.Embed()
        self.assertEqual("", embed_to_string(embed=embed))

        embed = discord.Embed(title="Hello", description="World")
        embed.set_footer(text="This is weird")
        embed.set_author(name="Its almost as if")
        embed.add_field(name="I am", value="Alive")
        embed.add_field(name="That would be weird tho", value="Right?")
        self.assertEqual(
            "Hello\nWorld\nThis is weird\nIts almost as if\nI am\nAlive\nThat would be weird tho\nRight?\n",
            embed_to_string(embed),
        )

    def test_dictToEmbed(self):
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

        self.assertEqual(embed.to_dict(), test_embed.to_dict())

    def test_transformMessage(self):
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

        self.assertEqual(embed.to_dict(), test_embed.to_dict())

        message = transform_message("Hello $MENTIONUSER", mock_message, warn_dict)
        self.assertEqual("Hello <@12345>", message)
