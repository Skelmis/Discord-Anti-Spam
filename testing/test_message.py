import sys
import unittest

sys.path.insert(0, "..")
from AntiSpam import Message


class TextMessage(unittest.TestCase):
    """
    Used to test the message object
    """

    def setUp(self):
        """
        Simply setup our message obj before usage
        """
        self.message = Message(0, "Hello world", 2, 3, 4)

    def test_intAssignment(self):
        self.assertIsInstance(self.message.id, int)
        self.assertIsInstance(self.message.guildId, int)
        self.assertIsInstance(self.message.channelId, int)
        self.assertIsInstance(self.message.authorId, int)

    def test_strAssignment(self):
        self.assertIsInstance(self.message.content, str)

    def test_idRaises(self):
        with self.assertRaises(ValueError):
            self.message.id = "String"

    def test_authorIdRaises(self):
        with self.assertRaises(ValueError):
            self.message.authorId = "String"

    def test_channelIdRaises(self):
        with self.assertRaises(ValueError):
            self.message.channelId = "String"

    def test_guildIdRaises(self):
        with self.assertRaises(ValueError):
            self.message.guildId = "String"

    @unittest.expectedFailure
    def test_contentRaises(self):
        with self.assertRaises(ValueError):
            self.message.content = {"key", "value"}
            self.message.content = 1


if __name__ == "__main__":
    unittest.main()
