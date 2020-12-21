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
import io
import logging
import sys
import unittest

from discord.ext import commands

from AntiSpam import AntiSpamHandler
from AntiSpam.Exceptions import DuplicateObject, BaseASHException, MissingGuildPermissions
from AntiSpam.static import Static
from AntiSpam.Guild import Guild
from AntiSpam.User import User
from testing.mocks.MockMember import get_mocked_member, get_mocked_bot
from testing.mocks.MockMessage import get_mocked_message


class TestAsh(unittest.TestCase):
    """
    Used to test the ASH object (AntiSpamHandler)
    """

    def setUp(self):
        """
        Simply setup our Ash obj before usage
        """
        self.ash = AntiSpamHandler(get_mocked_bot(name="bot", id=98987))
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

    def test_botAssignment(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(None)
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(1)
        
        with self.assertRaises(ValueError):
            AntiSpamHandler("1")

        with self.assertRaises(ValueError):
            AntiSpamHandler({1: 2})

        with self.assertRaises(ValueError):
            AntiSpamHandler([1, None])

        with self.assertRaises(ValueError):
            AntiSpamHandler(True)

        with self.assertRaises(ValueError):
            AntiSpamHandler(False)

        AntiSpamHandler(commands.Bot(command_prefix="!"))
    
    def test_warnThreshold(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), warn_threshold="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), warn_threshold=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), warn_threshold=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), warn_threshold=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), warn_threshold=1)
        AntiSpamHandler(commands.Bot(command_prefix="!"), warn_threshold=None)

    def test_kickThreshold(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), kick_threshold="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), kick_threshold=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), kick_threshold=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), kick_threshold=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), kick_threshold=1)
        AntiSpamHandler(commands.Bot(command_prefix="!"), kick_threshold=None)
    
    def test_banThreshold(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ban_threshold="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ban_threshold=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ban_threshold=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ban_threshold=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), ban_threshold=1)
        AntiSpamHandler(commands.Bot(command_prefix="!"), ban_threshold=None)
    
    def test_messageInterval(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_interval="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_interval=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_interval=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_interval=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), message_interval=1000)
        AntiSpamHandler(commands.Bot(command_prefix="!"), message_interval=None)

        with self.assertRaises(BaseASHException):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_interval=999)
    
    def test_guildKickMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message=1)
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message=dict())
    
    def test_guildBanMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=1)
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=dict())
    
    def test_userKickMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=1)
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=dict())
    
    def test_userBanMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=1)
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=dict())
    
    def test_messageDuplicateCount(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=[1])
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=2.0)

        AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=2)
        AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=None)
    
    def test_messageDuplicateAccuracy(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_accuracy="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_accuracy=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_accuracy=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_accuracy=[1])

        ash = AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_accuracy=2)
        AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_accuracy=None)

        self.assertIsInstance(ash.options.get("message_duplicate_accuracy"), float)

        AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_accuracy=2.0)
    
    def test_ignorePerms(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_perms="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_perms=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_perms=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_perms=1)

        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_perms=[1])
        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_perms=None)
    
    def test_ignoreUsers(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_users="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_users=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_users=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_users=1)

        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_users=[1])
        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_users=None)
    
    def test_ignoreChannels(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_channels="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_channels=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_channels=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_channels=1)

        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_channels=[1])
        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_channels=None)
    
    def test_ignoreRoles(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=1)

        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=[1])
        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=None)
    
    def test_ignoreGuilds(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_guilds="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_guilds=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_guilds=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_guilds=1)

        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_guilds=[1])
        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_guilds=None)
    
    def test_ignoreBots(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_bots="1")
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_bots=dict())
        
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_bots=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_bots=1)

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_bots=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_bots=True)
        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_bots=None)

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
        # Just tests this runs
        ash = AntiSpamHandler(commands.Bot(command_prefix="!"), guild_warn_message={})

    def test_deleteSpam(self):
        with self.assertRaises(ValueError):
            ash = AntiSpamHandler(commands.Bot(command_prefix="!"), delete_spam={})

        ash = AntiSpamHandler(commands.Bot(command_prefix="!"), delete_spam=True)

    def test_propagateRoleIgnoring(self):
        """
        Tests if the propagate method ignores the correct roles
        """
        ash = AntiSpamHandler(
            get_mocked_member(name="bot", id="87678"), ignore_roles=[151515]
        )

        result = ash.propagate(get_mocked_message())

        self.assertEqual(result["status"], "Ignoring this role: 151515")

    def test_propagateTypes(self):
        with self.assertRaises(ValueError):
            self.ash.propagate(1)

        with self.assertRaises(ValueError):
            self.ash.propagate(None)

        with self.assertRaises(ValueError):
            self.ash.propagate("Hi!")

        with self.assertRaises(ValueError):
            self.ash.propagate(True)

    def test_propagateDmIgnore(self):
        result = self.ash.propagate(get_mocked_message(is_in_guild=False))
        self.assertEqual(result["status"], "Ignoring messages from dm's")

    def test_propagateBotIgnore(self):
        result = self.ash.propagate(
            get_mocked_message(member_kwargs={"bot": True, "id": 98987})
        )
        self.assertEqual(result["status"], "Ignoring messages from myself (the bot)")

        result_two = self.ash.propagate(
            get_mocked_message(member_kwargs={"bot": True, "id": 98798})
        )
        self.assertEqual(result_two["status"], "Ignoring messages from bots")

    def test_propagateUserIgnore(self):
        self.ash.add_ignored_item(12345, "member")

        result = self.ash.propagate(get_mocked_message())
        self.assertEqual(result["status"], "Ignoring this user: 12345")

        result_two = self.ash.propagate(
            get_mocked_message(member_kwargs={"id": 5433221})
        )
        self.assertNotEqual(result_two["status"], "Ignoring this user: 12345")

    def test_propagateIgnoreGuild(self):
        self.ash.add_ignored_item(123456789, "guild")
        self.assertEqual(self.ash.options["ignore_guilds"], [123456789])

        result = self.ash.propagate(get_mocked_message())
        self.assertEqual(result["status"], "Ignoring this guild: 123456789")

        self.ash.remove_ignored_item(123456789, "guild")
        self.assertEqual(self.ash.options["ignore_guilds"], [])
    
    def test_propagateIgnoredChannel(self):
        self.ash.add_ignored_item(98987, "channel")
        self.assertEqual(self.ash.options['ignore_channels'], [98987])

        result = self.ash.propagate(get_mocked_message())
        self.assertEqual(result['status'], "Ignoring this channel: 98987")

        self.ash.remove_ignored_item(98987, "channel")
        self.assertEqual(self.ash.options['ignore_channels'], [])

    def test_propagateGuildCreation(self):
        self.assertEqual(len(self.ash.guilds), 2)
        self.ash.propagate(get_mocked_message(guild_kwargs={"id": 15}))
        self.assertEqual(len(self.ash.guilds), 2)

        self.ash.propagate(get_mocked_message())
        self.assertEqual(len(self.ash.guilds), 3)
    
    def test_propagateGuildPerms(self):
        ash = AntiSpamHandler(get_mocked_bot())
        message = get_mocked_message()
        message.guild.me.guild_permissions.kick_members = False
        message.guild.me.guild_permissions.ban_members = True
        with self.assertRaises(MissingGuildPermissions, msg="Invalid kick_members perms"):
            ash.propagate(message)
        
        message.guild.me.guild_permissions.kick_members = True
        message.guild.me.guild_permissions.ban_members = False
        with self.assertRaises(MissingGuildPermissions, msg="Invalid ban_members perms"):
            ash.propagate(message)
        
        message.guild.me.guild_permissions.ban_members = True
        ash.propagate(message)



# TODO In test assignments, test it actually get assigned to the options dict