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
import asyncio
import unittest
import discord

from discord.ext import commands

from AntiSpam import AntiSpamHandler
from AntiSpam.Exceptions import (
    DuplicateObject,
    BaseASHException,
    MissingGuildPermissions,
    LogicError,
)
from AntiSpam.static import Static
from AntiSpam.Guild import Guild
from AntiSpam.User import User
from testing.mocks.MockMember import MockedMember
from testing.mocks.MockMessage import MockedMessage

from json_loader import read_json, write_json


class TestAsh(unittest.IsolatedAsyncioTestCase):
    """
    Used to test the ASH object (AntiSpamHandler)
    """

    async def asyncSetUp(self):
        """
        Simply setup our Ash obj before usage
        """
        self.ash = AntiSpamHandler(
            MockedMember(name="bot", member_id=98987, mock_type="bot").to_mock()
        )
        self.ash.guilds = Guild(None, 12, Static.DEFAULTS)
        self.ash.guilds = Guild(None, 15, Static.DEFAULTS)

    async def test_defaults(self):
        self.assertEqual(self.ash.options, Static.DEFAULTS)

    async def test_properties(self):
        with self.assertRaises(ValueError):
            self.ash.guilds = "1"

        with self.assertRaises(DuplicateObject):
            self.ash.guilds = Guild(None, 15, Static.DEFAULTS)

    async def test_messageAccuracyType(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy="x"
            )

    async def test_messageAccuracyRange(self):
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

    async def test_messageAccuracyAssignment(self):
        ash = AntiSpamHandler(
            commands.Bot(command_prefix="!"), message_duplicate_accuracy=50
        )
        self.assertEqual(ash.options["message_duplicate_accuracy"], 50)

    async def test_botAssignment(self):
        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            AntiSpamHandler(None)

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            AntiSpamHandler(1)

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            AntiSpamHandler("1")

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            AntiSpamHandler({1: 2})

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            AntiSpamHandler([1, None])

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            AntiSpamHandler(True)

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            AntiSpamHandler(False)

        AntiSpamHandler(commands.Bot(command_prefix="!"))
        AntiSpamHandler(commands.AutoShardedBot(command_prefix="!"))
        AntiSpamHandler(discord.Client())
        AntiSpamHandler(discord.AutoShardedClient())

    async def test_warnThreshold(self):
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

    async def test_kickThreshold(self):
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

    async def test_banThreshold(self):
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

    async def test_messageInterval(self):
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

    async def test_guildKickMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message=1)

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), guild_kick_message=tuple()
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_kick_message=dict())

    async def test_guildBanMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=1)

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_ban_message=dict())

    async def test_userKickMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=1)

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), user_kick_message=dict())

    async def test_userBanMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=1)

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=[1])

        AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message="hi")
        AntiSpamHandler(commands.Bot(command_prefix="!"), user_ban_message=dict())

    async def test_userFailedKickMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), user_failed_kick_message=1
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), user_failed_kick_message=tuple()
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), user_failed_kick_message=[1]
            )

        AntiSpamHandler(commands.Bot(command_prefix="!"), user_failed_kick_message="hi")
        AntiSpamHandler(
            commands.Bot(command_prefix="!"), user_failed_kick_message=dict()
        )

    async def test_userFailedBanMessage(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), user_failed_ban_message=1)

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), user_failed_ban_message=tuple()
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), user_failed_ban_message=[1]
            )

        AntiSpamHandler(commands.Bot(command_prefix="!"), user_failed_ban_message="hi")
        AntiSpamHandler(
            commands.Bot(command_prefix="!"), user_failed_ban_message=dict()
        )

    async def test_messageDuplicateCount(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_count="1"
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_count=dict()
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_count=tuple()
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_count=[1]
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_count=2.0
            )

        AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=2)
        AntiSpamHandler(commands.Bot(command_prefix="!"), message_duplicate_count=None)

    async def test_messageDuplicateAccuracy(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy="1"
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy=dict()
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy=tuple()
            )

        with self.assertRaises(ValueError):
            AntiSpamHandler(
                commands.Bot(command_prefix="!"), message_duplicate_accuracy=[1]
            )

        ash = AntiSpamHandler(
            commands.Bot(command_prefix="!"), message_duplicate_accuracy=2
        )
        AntiSpamHandler(
            commands.Bot(command_prefix="!"), message_duplicate_accuracy=None
        )

        self.assertIsInstance(ash.options.get("message_duplicate_accuracy"), float)

        AntiSpamHandler(
            commands.Bot(command_prefix="!"), message_duplicate_accuracy=2.0
        )

    async def test_ignorePerms(self):
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

    async def test_ignoreUsers(self):
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

    async def test_ignoreChannels(self):
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

    async def test_ignoreRoles(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles="1")

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=dict())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=tuple())

        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=1)

        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=[1, "test role"])
        AntiSpamHandler(commands.Bot(command_prefix="!"), ignore_roles=None)

    async def test_ignoreGuilds(self):
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

    async def test_ignoreBots(self):
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

    # TODO Add a ensureRaises test for each set-able option...
    # TODO Capture standard out and ensure the logger is working,
    #      but only at the correct levels

    async def test_guildWarnMessageType(self):
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

    async def test_guildWarnMessageString(self):
        ash = AntiSpamHandler(
            commands.Bot(command_prefix="!"), guild_warn_message="This is a message"
        )
        self.assertEqual(ash.options["guild_warn_message"], "This is a message")

    async def test_guildWarnMessageEmbed(self):
        # Just tests this runs
        AntiSpamHandler(commands.Bot(command_prefix="!"), guild_warn_message={})

    async def test_deleteSpam(self):
        with self.assertRaises(ValueError):
            AntiSpamHandler(commands.Bot(command_prefix="!"), delete_spam={})

        AntiSpamHandler(commands.Bot(command_prefix="!"), delete_spam=True)

    async def test_propagateRoleIgnoring(self):
        """
        Tests if the propagate method ignores the correct roles
        """
        ash = AntiSpamHandler(
            MockedMember(name="bot", member_id=87678).to_mock(), ignore_roles=[151515]
        )
        print(MockedMember(mock_type="bot").to_mock().user.id)
        result = await ash.propagate(MockedMessage().to_mock())

        self.assertEqual(result["status"], "Ignoring this role: 151515")

    async def test_propagateTypes(self):
        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            await self.ash.propagate(1)

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            await self.ash.propagate(None)

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            await self.ash.propagate("Hi!")

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            await self.ash.propagate(True)

    async def test_propagateDmIgnore(self):
        result = await self.ash.propagate(MockedMessage(is_in_guild=False).to_mock())
        self.assertEqual(result["status"], "Ignoring messages from dm's")

    async def test_propagateBotIgnore(self):
        result = await self.ash.propagate(
            MockedMessage(author_is_bot=True, author_id=98987).to_mock()
        )
        self.assertEqual(result["status"], "Ignoring messages from myself (the bot)")

        result_two = await self.ash.propagate(
            MockedMessage(author_is_bot=True, author_id=98798).to_mock()
        )
        self.assertEqual(result_two["status"], "Ignoring messages from bots")

    async def test_propagateUserIgnore(self):
        self.ash.add_ignored_item(12345, "member")

        result = await self.ash.propagate(MockedMessage().to_mock())
        self.assertEqual(result["status"], "Ignoring this user: 12345")

        result_two = await self.ash.propagate(
            MockedMessage(author_id=5433221).to_mock()
        )
        self.assertNotEqual(result_two["status"], "Ignoring this user: 12345")

    async def test_propagateIgnoreGuild(self):
        self.ash.add_ignored_item(123456789, "guild")
        self.assertEqual(self.ash.options["ignore_guilds"], [123456789])

        result = await self.ash.propagate(MockedMessage().to_mock())
        self.assertEqual(result["status"], "Ignoring this guild: 123456789")

        self.ash.remove_ignored_item(123456789, "guild")
        self.assertEqual(self.ash.options["ignore_guilds"], [])

    async def test_propagateIgnoredChannel(self):
        self.ash.add_ignored_item(98987, "channel")
        self.assertEqual(self.ash.options["ignore_channels"], [98987])

        result = await self.ash.propagate(MockedMessage().to_mock())
        self.assertEqual(result["status"], "Ignoring this channel: 98987")

        self.ash.remove_ignored_item(98987, "channel")
        self.assertEqual(self.ash.options["ignore_channels"], [])

    async def test_propagateGuildCreation(self):
        self.assertEqual(len(self.ash.guilds), 2)
        await self.ash.propagate(MockedMessage(guild_id=15).to_mock())
        self.assertEqual(len(self.ash.guilds), 2)

        await self.ash.propagate(MockedMessage().to_mock())
        self.assertEqual(len(self.ash.guilds), 3)

    async def test_propagateGuildPerms(self):
        ash = AntiSpamHandler(MockedMember(mock_type="bot").to_mock())
        message = MockedMessage().to_mock()
        message.guild.me.guild_permissions.kick_members = False
        message.guild.me.guild_permissions.ban_members = True
        with self.assertRaises(
            MissingGuildPermissions, msg="Invalid kick_members perms"
        ):
            await ash.propagate(message)

        message.guild.me.guild_permissions.kick_members = True
        message.guild.me.guild_permissions.ban_members = False
        with self.assertRaises(
            MissingGuildPermissions, msg="Invalid ban_members perms"
        ):
            await ash.propagate(message)

        message.guild.me.guild_permissions.ban_members = True
        await ash.propagate(message)

    async def test_ignoreMethods(self):
        self.assertEqual(self.ash.options["ignore_users"], [])
        self.assertEqual(self.ash.options["ignore_channels"], [])
        self.assertEqual(self.ash.options["ignore_perms"], [8])
        self.assertEqual(self.ash.options["ignore_guilds"], [])
        self.assertEqual(self.ash.options["ignore_roles"], [])

        self.ash.add_ignored_item(1, "member")
        self.ash.add_ignored_item(2, "channel")
        self.ash.add_ignored_item(3, "perm")
        self.ash.add_ignored_item(4, "guild")
        self.ash.add_ignored_item(5, "role")

        self.assertEqual(self.ash.options["ignore_users"], [1])
        self.assertEqual(self.ash.options["ignore_channels"], [2])
        self.assertEqual(self.ash.options["ignore_perms"], [8, 3])
        self.assertEqual(self.ash.options["ignore_guilds"], [4])
        self.assertEqual(self.ash.options["ignore_roles"], [5])

        self.ash.remove_ignored_item(1, "member")
        self.ash.remove_ignored_item(2, "channel")
        self.ash.remove_ignored_item(3, "perm")
        self.ash.remove_ignored_item(4, "guild")
        self.ash.remove_ignored_item(5, "role")

        self.assertEqual(self.ash.options["ignore_users"], [])
        self.assertEqual(self.ash.options["ignore_channels"], [])
        self.assertEqual(self.ash.options["ignore_perms"], [8])
        self.assertEqual(self.ash.options["ignore_guilds"], [])
        self.assertEqual(self.ash.options["ignore_roles"], [])

    async def test_ignoreMethodExceptions(self):
        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            self.ash.add_ignored_item("LOL", "test")

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            self.ash.remove_ignored_item("LOL", "test")

        with self.assertRaises(BaseASHException):
            self.ash.add_ignored_item(1, "testing")

        with self.assertRaises(BaseASHException):
            self.ash.remove_ignored_item(1, "testing")

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            self.ash.add_ignored_item(1, [])

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            self.ash.remove_ignored_item(1, [])

    async def test_customGuildOptions(self):
        self.assertEqual(self.ash.guilds[0].options, Static.DEFAULTS)
        self.ash.add_custom_guild_options(self.ash.guilds[0].id, warn_threshold=15)
        self.assertNotEqual(self.ash.guilds[0].options, Static.DEFAULTS)
        self.assertEqual(self.ash.guilds[0].has_custom_options, True)

        self.ash.remove_custom_guild_options(self.ash.guilds[0].id)
        self.assertEqual(self.ash.guilds[0].options, Static.DEFAULTS)

        options = self.ash.get_guild_options(self.ash.guilds[0].id)[0]
        self.assertEqual(options, self.ash.guilds[0].options)
        self.assertEqual(options, self.ash.options)

    async def test_ASHRandomVar(self):
        with self.assertRaises(TypeError):
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), lol=1)

        with self.assertRaises(TypeError):
            self.ash.add_custom_guild_options(1234, testing=1)

    async def test_warnOnly(self):
        ash = AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), warn_only=True)
        self.assertEqual(ash.options["warn_only"], True)
        self.assertEqual(self.ash.options["warn_only"], False)

        ash = AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), warn_only=None)
        self.assertEqual(ash.options["warn_only"], False)

        with self.assertRaises(ValueError):
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), warn_only=1)

        with self.assertRaises(ValueError):
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), warn_only="1")

        with self.assertRaises(ValueError):
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), warn_only=dict())

        with self.assertRaises(ValueError):
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), warn_only=[])

    async def test_resetWarnCounter(self):
        # GIVEN / SETUP
        user = User(
            MockedMember(mock_type="bot").to_mock(), 123454321, 12, Static.DEFAULTS
        )
        self.ash.guilds[0].users = user
        self.assertEqual(1, len(self.ash.guilds[0].users))
        self.assertEqual(0, self.ash.guilds[0].users[0].warn_count)
        self.ash.guilds[0].users[0].warn_count += 1
        self.assertEqual(1, self.ash.guilds[0].users[0].warn_count)

        # WHEN / TESTING
        self.ash.reset_user_count(123454321, 12, Static.WARNCOUNTER)

        # THEN / ASSERTIONS
        self.assertEqual(0, self.ash.guilds[0].users[0].warn_count)

    async def test_resetKickCounter(self):
        # GIVEN / SETUP
        user = User(
            MockedMember(mock_type="bot").to_mock(), 123454321, 12, Static.DEFAULTS
        )
        self.ash.guilds[0].users = user
        self.assertEqual(1, len(self.ash.guilds[0].users))
        self.assertEqual(0, self.ash.guilds[0].users[0].kick_count)
        self.ash.guilds[0].users[0].kick_count += 1
        self.assertEqual(1, self.ash.guilds[0].users[0].kick_count)

        # WHEN / TESTING
        self.ash.reset_user_count(123454321, 12, Static.KICKCOUNTER)

        # THEN / ASSERTIONS
        self.assertEqual(0, self.ash.guilds[0].users[0].kick_count)

    async def test_resetCountersRaises(self):
        # SETUP
        user = User(
            MockedMember(mock_type="bot").to_mock(), 123454321, 12, Static.DEFAULTS
        )
        self.ash.guilds[0].users = user

        # ASSERTIONS / TESTING
        with self.assertRaises(LogicError):
            self.ash.reset_user_count(123454321, 12, "Who knows")

        # Invalid guild, should work silently
        self.ash.reset_user_count(123454321, 15, "Who knows")

        # Invalid user, should work silently
        self.ash.reset_user_count(1234, 12, "Who knows")

        # Invalid both, should work silently
        self.ash.reset_user_count(1234, 15, "Who knows")

    async def test_ensureOptionsRaisingModes(self):
        with self.assertRaises(BaseASHException):
            self.ash._ensure_options(warn_only=True, no_punish=True)

        self.ash._ensure_options(warn_only=False, no_punish=True)
        self.ash._ensure_options(warn_only=True, no_punish=False)

    async def test_noPunishMode(self):
        # SETUP
        ash = AntiSpamHandler(MockedMember(mock_type="bot").to_mock(), no_punish=True)

        # WHEN / TESTING
        data = []
        for num in range(6):
            return_value = await ash.propagate(MockedMessage(message_id=num).to_mock())
            data.append(return_value)

        # THEN / ASSERTIONS
        self.assertEqual(len(data), 6)

        # TODO Fix this while fixing #39
        self.assertEqual(data[0]["should_be_punished_this_message"], False)
        self.assertEqual(data[2]["should_be_punished_this_message"], False)
        self.assertEqual(data[3]["should_be_punished_this_message"], True)
        self.assertEqual(data[5]["should_be_punished_this_message"], True)

    @unittest.expectedFailure  # Not sure why, but adding ignored users appears to interact accross tests
    async def test_statefulLoading(self):
        data = read_json("unittests")
        test_ash = await AntiSpamHandler.load_from_dict(
            MockedMember(name="bot", member_id=98987, mock_type="bot").to_mock(), data
        )
        result = await test_ash.save_to_dict()
        self.assertEqual(data, result)


# TODO test delete_after options
