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

from AntiSpam import AntiSpamHandler, AntiSpamTracker, UserNotFound
from testing.mocks.MockMember import get_mocked_bot
from testing.mocks.MockMessage import get_mocked_message


class TestAsh(unittest.IsolatedAsyncioTestCase):
    async def test_initialization(self):
        # Test AntiSpamHandler type assertion
        with self.assertRaises(TypeError):
            AntiSpamTracker(1, 2)

        AntiSpamTracker(AntiSpamHandler(get_mocked_bot()), 3)

        with self.assertRaises(TypeError):
            AntiSpamTracker()

        ash = AntiSpamHandler(get_mocked_bot())
        message_interval = ash.options.get("message_interval")
        ast = AntiSpamTracker(ash, 3)
        self.assertEqual(message_interval, ast.valid_global_interval)

        ast = AntiSpamTracker(ash, 3, 15000)
        self.assertNotEqual(message_interval, ast.valid_global_interval)
        self.assertEqual(15000, ast.valid_global_interval)

        self.assertEqual(False, bool(ast.user_tracking))

        self.assertEqual(ast.punish_min_amount, 3)

        with self.assertRaises(TypeError):
            AntiSpamTracker(ash, 3, dict())

    async def test_updateCache(self):
        ast = AntiSpamTracker(AntiSpamHandler(get_mocked_bot()), 3)

        self.assertEqual(False, bool(ast.user_tracking))
        ast.update_cache(
            get_mocked_message(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(True, bool(ast.user_tracking))

        ast.user_tracking = {}  # overwrite so we can test more

        self.assertEqual(False, bool(ast.user_tracking))
        ast.update_cache(
            get_mocked_message(), {"should_be_punished_this_message": False}
        )
        self.assertEqual(False, bool(ast.user_tracking))

        with self.assertRaises(TypeError):
            ast.update_cache(1, dict())

        with self.assertRaises(TypeError):
            ast.update_cache(get_mocked_message(), 1)

        ast.user_tracking = {}
        self.assertEqual(0, len(ast.user_tracking))

        ast.update_cache(
            get_mocked_message(), {"should_be_punished_this_message": True}
        )
        ast.update_cache(
            get_mocked_message(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(1, len(ast.user_tracking))
        self.assertEqual(1, len(ast.user_tracking[123456789]))
        self.assertEqual(2, len(ast.user_tracking[123456789][12345]))

    async def test_getUserCount(self):
        ast = AntiSpamTracker(AntiSpamHandler(get_mocked_bot()), 3)
        ast.update_cache(
            get_mocked_message(), {"should_be_punished_this_message": True}
        )

        user_count = ast.get_user_count(get_mocked_message())

        self.assertEqual(user_count, 1)

        for i in range(3):
            ast.update_cache(
                get_mocked_message(), {"should_be_punished_this_message": True}
            )
        user_count = ast.get_user_count(get_mocked_message())
        self.assertEqual(user_count, 4)

        with self.assertRaises(UserNotFound):
            message = get_mocked_message(guild_kwargs={"id": 15})
            ast.get_user_count(message)

        with self.assertRaises(UserNotFound):
            message = get_mocked_message(member_kwargs={"id": 25})
            ast.get_user_count(message)

    async def test_removeOutdatedTimestamps(self):
        ast = AntiSpamTracker(AntiSpamHandler(get_mocked_bot()), 3, 50)
        ast.update_cache(
            get_mocked_message(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(ast.get_user_count(get_mocked_message()), 1)

        ast.remove_outdated_timestamps(123456789, 12345)
        self.assertEqual(ast.get_user_count(get_mocked_message()), 1)

        await asyncio.sleep(0.06)
        ast.remove_outdated_timestamps(123456789, 12345)
        self.assertEqual(ast.get_user_count(get_mocked_message()), 0)

    async def test_cleanCache(self):
        ast = AntiSpamTracker(AntiSpamHandler(get_mocked_bot()), 3, 50)
        ast.update_cache(
            get_mocked_message(), {"should_be_punished_this_message": True}
        )
        self.assertEqual(1, len(ast.user_tracking[123456789][12345]))

        ast.clean_cache()
        self.assertEqual(len(ast.user_tracking), 1)
        self.assertEqual(1, len(ast.user_tracking[123456789][12345]))

        await asyncio.sleep(0.06)
        # This should now fully clean the cache
        ast.clean_cache()

        self.assertEqual(ast.user_tracking, dict())
