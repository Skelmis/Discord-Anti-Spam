import sys
import unittest

from AntiSpam.Exceptions import DuplicateObject, ObjectMismatch

sys.path.insert(0, "..")
from AntiSpam import Guild, User, Message


class TestGuild(unittest.TestCase):
    """
    Used to test the Guild object
    """

    def setUp(self):
        """
        Simply setup our Guild obj before usage
        """
        self.guild = Guild(None, 15, {})
        self.guild.users = User(20, 15, {})
        self.guild.users = User(21, 15, {})

    def test_intAssignment(self):
        self.assertEqual(self.guild.id, 15)

    def test_listAssignment(self):
        self.assertIsInstance(self.guild.users, list)

    def test_valueAssignment(self):
        self.assertEqual(self.guild.id, 15)

        self.guild.id = 10

        self.assertEqual(self.guild.id, 10)

    def test_userAssignment(self):
        self.assertEqual(len(self.guild.users), 2)
        self.guild.users = User(22, 15, {})
        self.assertEqual(len(self.guild.users), 3)

    def test_userRaises(self):
        with self.assertRaises(ValueError):
            self.guild.users = 1

    def test_userRaisesDuplicate(self):
        with self.assertRaises(DuplicateObject):
            self.guild.users = User(21, 15, {})

    def test_messageRaisesMismatch(self):
        with self.assertRaises(ObjectMismatch):
            self.guild.users = User(22, 16, {})


if __name__ == "__main__":
    unittest.main()
