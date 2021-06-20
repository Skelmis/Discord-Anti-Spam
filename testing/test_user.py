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
import datetime
import unittest
from copy import deepcopy

from discord.ext.antispam.caches.memory.user import User
from discord.ext.antispam import Message
from discord.ext.antispam import Static
from discord.ext.antispam import DuplicateObject, ObjectMismatch, LogicError
from testing.mocks.MockChannel import MockedChannel
from testing.mocks.MockMessage import MockedMessage


class TestUser(unittest.IsolatedAsyncioTestCase):
    """
    Used to test the user object
    """

    async def asyncSetUp(self):
        """
        Simply setup our User obj before usage
        """
        self.user = User(None, 0, 3, Static.DEFAULTS)
        self.user.messages = Message(0, "Hello world", 0, 2, 3)
        self.user.messages = Message(1, "Foo Bar", 0, 2, 3)

    async def test_botAssignment(self):
        # Given we don't want to populate an entire bot,
        # lets just check its assigned correctly
        self.assertIsNone(self.user.bot)

    async def test_intAssignment(self):
        self.assertIsInstance(self.user.id, int)
        self.assertIsInstance(self.user.guild_id, int)

    async def test_listAssignment(self):
        self.assertIsInstance(self.user.messages, list)

    async def test_dictAssignment(self):
        self.assertIsInstance(self.user.options, dict)

    async def test_valueAssignment(self):
        self.assertEqual(self.user.id, 0)
        self.assertEqual(self.user.guild_id, 3)
        self.assertEqual(self.user.options, Static.DEFAULTS)

        self.user.id = 10
        self.user.guild_id = 10

        self.assertEqual(self.user.id, 10)
        self.assertEqual(self.user.guild_id, 10)

    async def test_properties(self):
        with self.assertRaises(ValueError):
            self.user.id = "1"

        with self.assertRaises(ValueError):
            self.user.guild_id = "1"

    async def test_messageAssignment(self):
        self.assertEqual(len(self.user.messages), 2)
        self.user.messages = Message(3, "Test", 0, 2, 3)
        self.assertEqual(len(self.user.messages), 3)

    async def test_messageRaises(self):
        with self.assertRaises(ValueError):
            self.user.messages = 1

    async def test_messageRaisesDuplicate(self):
        with self.assertRaises(DuplicateObject):
            self.user.messages = Message(1, "Testing", 0, 2, 3)

    async def test_messageRaisesMismatch(self):
        with self.assertRaises(ObjectMismatch):
            self.user.messages = Message(20, "Testing", 20, 20, 20)

    async def test_repr(self):
        self.assertEqual(
            repr(self.user),
            (
                f"'{self.user.__class__.__name__} object. User id: {self.user.id}, Guild id: {self.user.guild_id}, "
                f"Len Stored Messages {len(self.user.messages)}'"
            ),
        )

    async def test_str(self):
        self.assertEqual(
            str(self.user), f"{self.user.__class__.__name__} object for {self.user.id}."
        )

    async def test_eqEqual(self):
        obj = User(None, 0, 3, Static.DEFAULTS)
        self.assertTrue(self.user == obj)

    async def test_eqNotEqual(self):
        obj = User(None, 2, 2, Static.DEFAULTS)
        self.assertFalse(self.user == obj)

    async def test_eqRaises(self):
        with self.assertRaises(ValueError):
            self.assertFalse(self.user == 1)

    async def test_duplicateCounter(self):
        self.assertNotEqual(
            self.user.duplicate_counter, self.user.get_correct_duplicate_count()
        )

        self.assertEqual(
            self.user.duplicate_counter - 1, self.user.get_correct_duplicate_count()
        )

    async def test_cleanUp(self):
        x = len(self.user.messages)
        self.user.clean_up(datetime.datetime.now(datetime.timezone.utc))
        self.assertEqual(x, len(self.user.messages))

    async def test__increment_duplicate_count(self):
        self.assertEqual(self.user.duplicate_counter, 1)
        self.user._increment_duplicate_count(Message(2, "A test message", 0, 2, 3))
        self.assertEqual(self.user.duplicate_counter, 2)

        self.user._increment_duplicate_count(Message(2, "A test message", 0, 2, 3), 2)
        self.assertEqual(self.user.duplicate_counter, 4)

        self.user.options["per_channel_spam"] = True
        self.assertEqual(self.user.duplicate_channel_counter_dict, dict())

        self.user._increment_duplicate_count(Message(2, "A test message", 0, 2, 3))

        self.assertEqual(self.user.duplicate_channel_counter_dict, {2: 2})
        self.user._increment_duplicate_count(Message(2, "A test message", 0, 2, 3), 2)
        self.assertEqual(self.user.duplicate_channel_counter_dict, {2: 4})

    async def test__get_duplicate_count(self):
        result = self.user._get_duplicate_count(Message(3, "A test message", 0, 2, 3))
        self.assertEqual(result, 1)

        self.user.options["per_channel_spam"] = True
        result = self.user._get_duplicate_count(Message(3, "A test message", 0, 2, 3))
        self.assertEqual(result, 1)

        self.user._increment_duplicate_count(Message(2, "A test message", 0, 2, 3))
        self.user._increment_duplicate_count(Message(2, "A test message", 0, 2, 3))
        result = self.user._get_duplicate_count(Message(3, "A test message", 0, 2, 3))
        self.assertEqual(result, 3)

        # This channel shouldn't exist / have duplicates
        result = self.user._get_duplicate_count(Message(3, "A test message", 0, 1, 3))
        self.assertEqual(result, 1)

        with self.assertRaises(LogicError):
            # noinspection PyTypeChecker
            self.user._get_duplicate_count("hi")

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            self.user._get_duplicate_count(channel_id=dict())

        with self.assertRaises(LogicError):
            # noinspection PyTypeChecker
            self.user._get_duplicate_count()

    async def test__remove_duplicate_count(self):
        self.assertEqual(self.user.duplicate_counter, 1)
        self.user._remove_duplicate_count(Message(2, "A test message", 0, 2, 3))
        self.assertEqual(self.user.duplicate_counter, 0)

        self.user.options["per_channel_spam"] = True
        msg = Message(2, "A test message", 0, 2, 3)
        self.user._increment_duplicate_count(msg)
        self.user._increment_duplicate_count(msg)
        self.assertEqual(self.user._get_duplicate_count(msg), 3)

    async def test_propagatePunish(self):
        """Checks the propagate method tries to punish at correct times"""
        m = MockedMessage(message_id=0, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], False)

        m = MockedMessage(message_id=1, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], False)

        m = MockedMessage(message_id=2, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], False)

        m = MockedMessage(message_id=3, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], True)

        m = MockedMessage(message_id=4, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], True)

    async def test_propagateWarn(self):
        """Tests it warns for the correct amount"""
        for i in range(3):
            m = MockedMessage(message_id=i, author_id=0, guild_id=3).to_mock()
            data = await self.user.propagate(m)

        # Shouldn't be punished yet. But one off
        # noinspection PyUnboundLocalVariable
        self.assertEqual(data["should_be_punished_this_message"], False)

        m = MockedMessage(message_id=4, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], True)
        self.assertEqual(data["was_warned"], True)

        m = MockedMessage(message_id=5, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], True)
        self.assertEqual(data["was_warned"], True)

        m = MockedMessage(message_id=6, author_id=0, guild_id=3).to_mock()
        data = await self.user.propagate(m)
        self.assertEqual(data["should_be_punished_this_message"], True)
        self.assertEqual(data["was_warned"], False)
        self.assertEqual(data["was_kicked"], True)

    async def test_multiChannelSpam(self):
        options = deepcopy(Static.DEFAULTS)
        options["per_channel_spam"] = True

        user = User(None, 0, 3, options)
        for i in range(3):
            m = MockedMessage(message_id=i, author_id=0, guild_id=3).to_mock()
            m.channel = MockedChannel(channel_id=1).to_mock()
            await user.propagate(m)

        self.assertEqual(user.get_correct_duplicate_count(1), 3)

        message = MockedMessage(author_id=0, guild_id=3).to_mock()
        message.channel = MockedChannel(channel_id=2).to_mock()

        self.assertEqual(user.get_correct_duplicate_count(2), 0)

        for i in range(5):
            m = MockedMessage(message_id=i, author_id=0, guild_id=3).to_mock()
            m.channel = MockedChannel(channel_id=2).to_mock()
            await user.propagate(m)

        self.assertEqual(user.get_correct_duplicate_count(1), 3)
        self.assertEqual(user.get_correct_duplicate_count(2), 5)


if __name__ == "__main__":
    unittest.main()
