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

import sys
import unittest
import logging

from AntiSpam.Guild import Guild
from AntiSpam.User import User
from AntiSpam.static import Static
from AntiSpam.Exceptions import DuplicateObject, ObjectMismatch


class TestGuild(unittest.TestCase):
    """
    Used to test the Guild object
    """

    def setUp(self):
        """
        Simply setup our Guild obj before usage
        """
        self.guild = Guild(None, 15, Static.DEFAULTS)
        self.guild.users = User(None, 20, 15, Static.DEFAULTS)
        self.guild.users = User(None, 21, 15, Static.DEFAULTS)

    def test_intAssignment(self):
        self.assertEqual(self.guild.id, 15)

    def test_listAssignment(self):
        self.assertIsInstance(self.guild.users, list)

    def test_valueAssignment(self):
        self.assertEqual(self.guild.id, 15)

        self.guild.id = 10

        self.assertEqual(self.guild.id, 10)

    def test_properties(self):
        with self.assertRaises(ValueError):
            self.guild.id = "1"

    def test_userAssignment(self):
        self.assertEqual(len(self.guild.users), 2)
        self.guild.users = User(None, 22, 15, Static.DEFAULTS)
        self.assertEqual(len(self.guild.users), 3)

    def test_userRaises(self):
        with self.assertRaises(ValueError):
            self.guild.users = 1

    def test_userRaisesDuplicate(self):
        with self.assertRaises(DuplicateObject):
            self.guild.users = User(None, 21, 15, Static.DEFAULTS)

    def test_messageRaisesMismatch(self):
        with self.assertRaises(ObjectMismatch):
            self.guild.users = User(None, 22, 16, Static.DEFAULTS)

    def test_str(self):
        self.assertEqual(
            str(self.guild),
            f"{self.guild.__class__.__name__} object for {self.guild.id}.",
        )

    def test_repr(self):
        self.assertEqual(
            repr(self.guild),
            (
                f"'{self.guild.__class__.__name__} object. Guild id: {self.guild.id}, "
                f"Len Stored Users {len(self.guild._users)}'"
            ),
        )


if __name__ == "__main__":
    unittest.main()
