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

# TODO Make this
import asyncio
import unittest

from antispam import AntiSpamHandler, MemberNotFound
from antispam.plugins import AntiSpamTracker

from testing.mocks.MockMember import MockedMember
from testing.mocks.MockMessage import MockedMessage


class TestAsh(unittest.IsolatedAsyncioTestCase):
    # TODO Utilise the built_in setup func
    async def test_initialization(self):
        # Test AntiSpamHandler type assertion
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            AntiSpamTracker(1, 2)

        AntiSpamTracker(AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 3)

        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            AntiSpamTracker()

        ash = AntiSpamHandler(MockedMember(mock_type="bot").to_mock())
        message_interval = ash.options.get("message_interval")
        ast = AntiSpamTracker(ash, 3)
        self.assertEqual(message_interval, ast.valid_global_interval)

        ast = AntiSpamTracker(ash, 3, 15000)
        self.assertNotEqual(message_interval, ast.valid_global_interval)
        self.assertEqual(15000, ast.valid_global_interval)

        self.assertEqual(False, bool(ast.user_tracking))

        self.assertEqual(ast.punish_min_amount, 3)

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            AntiSpamTracker(ash, 3, dict())

    async def test_updateCache(self):
        ast = AntiSpamTracker(
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 3
        )

        ast.update_cache(
            MockedMessage(is_in_guild=False).to_mock(),
            {"should_be_punished_this_message": True},
        )

        self.assertEqual(False, bool(ast.user_tracking))
        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(True, bool(ast.user_tracking))

        ast.user_tracking = {}  # overwrite so we can test more

        self.assertEqual(False, bool(ast.user_tracking))
        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": False}
        )
        self.assertEqual(False, bool(ast.user_tracking))

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            ast.update_cache(1, dict())

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            ast.update_cache(MockedMessage().to_mock(), 1)

        ast.user_tracking = {}
        self.assertEqual(0, len(ast.user_tracking))

        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(1, len(ast.user_tracking))
        self.assertEqual(1, len(ast.user_tracking[123456789]))
        self.assertEqual(2, len(ast.user_tracking[123456789][12345]))

    async def test_getUserCount(self):
        ast = AntiSpamTracker(
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 3
        )
        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )

        user_count = ast.get_user_count(MockedMessage().to_mock())

        self.assertEqual(user_count, 1)

        for i in range(3):
            ast.update_cache(
                MockedMessage().to_mock(), {"should_be_punished_this_message": True}
            )
        user_count = ast.get_user_count(MockedMessage().to_mock())
        self.assertEqual(user_count, 4)

        with self.assertRaises(MemberNotFound):
            message = MockedMessage(guild_id=15).to_mock()
            ast.get_user_count(message)

        with self.assertRaises(MemberNotFound):
            message = MockedMessage(author_id=25).to_mock()
            ast.get_user_count(message)

    async def test_removeOutdatedTimestamps(self):
        ast = AntiSpamTracker(
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 3, 50
        )
        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(ast.get_user_count(MockedMessage().to_mock()), 1)

        ast.remove_outdated_timestamps(123456789, 12345)
        self.assertEqual(ast.get_user_count(MockedMessage().to_mock()), 1)

        await asyncio.sleep(0.06)
        ast.remove_outdated_timestamps(123456789, 12345)
        self.assertEqual(ast.get_user_count(MockedMessage().to_mock()), 0)

    async def test_cleanCache(self):
        ast = AntiSpamTracker(
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 3, 50
        )
        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(1, len(ast.user_tracking[123456789][12345]))

        ast.clean_cache()
        self.assertEqual(len(ast.user_tracking), 1)
        self.assertEqual(1, len(ast.user_tracking[123456789][12345]))

        await asyncio.sleep(0.06)
        # This should now fully clean the cache
        ast.clean_cache()

        self.assertEqual(ast.user_tracking, dict())

    async def test_getGuildValidInterval(self):
        ast = AntiSpamTracker(
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 3
        )
        self.assertEqual(ast._get_guild_valid_interval(123456789), 30000)
        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )

        self.assertEqual(ast._get_guild_valid_interval(123456789), 30000)

        ast.user_tracking[123456789]["valid_interval"] = 15000
        self.assertEqual(ast._get_guild_valid_interval(123456789), 15000)

    async def test_isSpamming(self):
        ast = AntiSpamTracker(
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 5
        )
        self.assertEqual(ast.is_spamming(MockedMessage().to_mock()), False)

        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(ast.is_spamming(MockedMessage().to_mock()), False)

        for i in range(3):
            ast.update_cache(
                MockedMessage().to_mock(), {"should_be_punished_this_message": True}
            )
        # Cap is 5, should have 4 messages rn
        self.assertEqual(ast.is_spamming(MockedMessage().to_mock()), False)
        self.assertEqual(4, len(ast.user_tracking[123456789][12345]))

        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(ast.is_spamming(MockedMessage().to_mock()), True)

        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(ast.is_spamming(MockedMessage().to_mock()), True)

    async def test_removePunishment(self):
        ast = AntiSpamTracker(
            AntiSpamHandler(MockedMember(mock_type="bot").to_mock()), 5
        )

        ast.remove_punishments(MockedMessage().to_mock())

        ast.update_cache(
            MockedMessage().to_mock(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(1, ast.get_user_count(MockedMessage().to_mock()))

        ast.remove_punishments(MockedMessage().to_mock())
        with self.assertRaises(MemberNotFound):
            ast.get_user_count(MockedMessage().to_mock())
