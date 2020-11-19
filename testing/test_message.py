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
import sys
import unittest

sys.path.insert(0, "..")
from AntiSpam import Message


class TestMessage(unittest.TestCase):
    """
    Used to test the Message object
    """

    def setUp(self):
        """
        Simply setup our Message obj before usage
        """
        self.message = Message(0, "Hello world", 2, 3, 4)

    def test_intAssignment(self):
        self.assertIsInstance(self.message.id, int)
        self.assertIsInstance(self.message.guild_id, int)
        self.assertIsInstance(self.message.channel_id, int)
        self.assertIsInstance(self.message.author_id, int)

    def test_strAssignment(self):
        self.assertIsInstance(self.message.content, str)

    def test_datetimeAssignment(self):
        self.assertIsInstance(self.message.creationTime, datetime.datetime)

    def test_valueAssignment(self):
        creationTime = self.message.creationTime

        self.assertEqual(self.message.id, 0)
        self.assertEqual(self.message.content, "Hello world")
        self.assertEqual(self.message.author_id, 2)
        self.assertEqual(self.message.channel_id, 3)
        self.assertEqual(self.message.guild_id, 4)
        self.assertFalse(self.message.is_duplicate)

        self.message.id = 10
        self.message.content = "Testing"
        self.message.author_id = 10
        self.message.channel_id = 10
        self.message.guild_id = 10
        self.message.creationTime = datetime.datetime.now()
        self.message.is_duplicate = True

        self.assertEqual(self.message.id, 10)
        self.assertEqual(self.message.content, "Testing")
        self.assertEqual(self.message.author_id, 10)
        self.assertEqual(self.message.channel_id, 10)
        self.assertEqual(self.message.guild_id, 10)
        self.assertEqual(self.message.creationTime, creationTime)
        self.assertTrue(self.message.is_duplicate)

    def test_idRaises(self):
        with self.assertRaises(ValueError):
            self.message.id = "String"

    def test_authorIdRaises(self):
        with self.assertRaises(ValueError):
            self.message.author_id = "String"

    def test_channelIdRaises(self):
        with self.assertRaises(ValueError):
            self.message.channel_id = "String"

    def test_guildIdRaises(self):
        with self.assertRaises(ValueError):
            self.message.guild_id = "String"

    @unittest.skip
    @unittest.expectedFailure
    def test_contentRaises(self):
        with self.assertRaises(ValueError):
            self.message.content = {"key", "value"}
            self.message.content = 1

    def test_str(self):
        self.assertEqual(
            str(self.message),
            f"{self.message.__class__.__name__} object - '{self.message.content}'",
        )

    def test_repr(self):
        self.assertEqual(
            repr(self.message),
            (
                f"'{self.message.__class__.__name__} object. Content: {self.message.content}, Message Id: {self.message.id}, "
                f"Author Id: {self.message.author_id}, Channel Id: {self.message.channel_id}, Guild Id: {self.message.guild_id} "
                f"Creation time: {self.message.creationTime}'"
            ),
        )

    def test_eqEqual(self):
        obj = Message(0, "Hello world", 2, 3, 4)
        self.assertTrue(self.message == obj)

    def test_eqNotEqual(self):
        obj = Message(1, "Hello world", 2, 3, 4)
        self.assertFalse(self.message == obj)


if __name__ == "__main__":
    unittest.main()
