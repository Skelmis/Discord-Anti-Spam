import sys
import unittest

from AntiSpam.Exceptions import DuplicateMessage

sys.path.insert(0, "..")
from AntiSpam import User, Message


class TestUser(unittest.TestCase):
    """
    Used to test the user object
    """

    def setUp(self):
        """
        Simply setup our message obj before usage
        """
        self.user = User(0, 3)
        self.user.messages = Message(0, "Hello world", 0, 2, 3)
        self.user.messages = Message(1, "Foo Bar", 0, 2, 3)

    def test_intAssignment(self):
        self.assertIsInstance(self.user.id, int)
        self.assertIsInstance(self.user.guildId, int)

    def test_listAssignment(self):
        self.assertIsInstance(self.user.messages, list)

    def test_valueAssignment(self):
        self.assertEqual(self.user.id, 0)
        self.assertEqual(self.user.guildId, 3)

        self.user.id = 10
        self.user.guildId = 10

        self.assertEqual(self.user.id, 10)
        self.assertEqual(self.user.guildId, 10)

    def test_messageAssignment(self):
        self.assertEqual(len(self.user.messages), 2)
        self.user.messages = Message(3, "Test", 0, 2, 3)
        self.assertEqual(len(self.user.messages), 3)

    def test_messageRaises(self):
        with self.assertRaises(ValueError):
            self.user.messages = 1

    def test_messageRaisesDuplicate(self):
        with self.assertRaises(DuplicateMessage):
            self.user.messages = Message(1, "Testing", 0, 2, 3)


if __name__ == "__main__":
    unittest.main()
