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
import logging
import unittest

from discord.ext import commands

from AntiSpam import AntiSpamHandler
from AntiSpam.Exceptions import DuplicateObject
from AntiSpam.static import Static
from AntiSpam.Guild import Guild
from AntiSpam.User import User


class TestGuild(unittest.TestCase):
    """
    Used to test the ASH object (AntiSpamHandler)
    """

    def setUp(self):
        """
        Simply setup our Guild obj before usage
        """
        self.ash = AntiSpamHandler(commands.Bot(command_prefix="!"))
        self.ash.guilds = Guild(
            None, 12, Static.DEFAULTS, logger=logging.getLogger(__name__)
        )
        self.ash.guilds = Guild(
            None, 15, Static.DEFAULTS, logger=logging.getLogger(__name__)
        )

    def test_defaults(self):
        self.assertEqual(self.ash.options, Static.DEFAULTS)

    def test_properties(self):
        with self.assertRaises(ValueError):
            self.ash.guilds = "1"

        with self.assertRaises(DuplicateObject):
            self.ash.guilds = Guild(
                None, 15, Static.DEFAULTS, logger=logging.getLogger(__name__)
            )

    def test_verboseType(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), verbose_level="x")

        ash = AntiSpamHandler(commands.Bot(command_prefix="!"), verbose_level=1)
        self.assertIsNotNone(ash)

    def test_verboseLevelRange(self):
        with self.assertRaises(ValueError, msg="Invalid verbose level (To low)"):
            AntiSpamHandler(commands.Bot(command_prefix="!"), verbose_level=-1)

        with self.assertRaises(ValueError, msg="Invalid verbose level (To high)"):
            AntiSpamHandler(commands.Bot(command_prefix="!"), verbose_level=6)

    def test_verboseAssignment(self):
        ash = AntiSpamHandler(commands.Bot(command_prefix="!"), verbose_level=4)
        self.assertEqual(ash.logger.level, 40)

    def test_messageAccuracyType(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy="x"
            )

    def test_messageAccuracyRange(self):
        with self.assertRaises(
            ValueError, msg="Invalid message_duplicate_accuracy (To low)"
        ):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy=0
            )

        with self.assertRaises(
            ValueError, msg="Invalid message_duplicate_accuracy (To high)"
        ):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy=101
            )

    def test_messageAccuracyAssignment(self):
        ash = AntiSpamHandler(
            commands.Bot(command_prefix="!"), message_duplicate_accuracy=50
        )
        self.assertEqual(ash.options["message_duplicate_accuracy"], 50)

    # TODO Add a ensureRaises test for each setable option...
    # TODO Capture standard out and ensure the logger is working,
    #      but only at the correct levels

    def test_guildWarnMessageType(self):
        with self.assertRaises(
            ValueError, msg="guild_warn_message should raise, given int"
        ):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_warn_message=1)

        with self.assertRaises(
            ValueError, msg="guild_warn_message should raise, given bool"
        ):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_warn_message=True)

        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_warn_message="Test")
        AntiSpamHandler(
            commands.Bot(command_prefix="!"), guild_warn_message={"title": "Hello!"}
        )

    def test_guildWarnMessageString(self):
        ash = AntiSpamHandler(
            commands.Bot(command_prefix="!"), guild_warn_message="This is a message"
        )
        self.assertEqual(ash.options["guild_warn_message"], "This is a message")

    def test_guildWarnMessageEmbed(self):
        ash = AntiSpamHandler(commands.Bot(command_prefix="!"), guild_warn_message={})
