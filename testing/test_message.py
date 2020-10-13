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
        self.assertIsInstance(self.message.guildId, int)
        self.assertIsInstance(self.message.channelId, int)
        self.assertIsInstance(self.message.authorId, int)

    def test_strAssignment(self):
        self.assertIsInstance(self.message.content, str)

    def test_datetimeAssignment(self):
        self.assertIsInstance(self.message.creationTime, datetime.datetime)

    def test_valueAssignment(self):
        creationTime = self.message.creationTime

        self.assertEqual(self.message.id, 0)
        self.assertEqual(self.message.content, "Hello world")
        self.assertEqual(self.message.authorId, 2)
        self.assertEqual(self.message.channelId, 3)
        self.assertEqual(self.message.guildId, 4)
        self.assertFalse(self.message.isDuplicate)

        self.message.id = 10
        self.message.content = "Testing"
        self.message.authorId = 10
        self.message.channelId = 10
        self.message.guildId = 10
        self.message.creationTime = datetime.datetime.now()
        self.message.isDuplicate = True

        self.assertEqual(self.message.id, 10)
        self.assertEqual(self.message.content, "Testing")
        self.assertEqual(self.message.authorId, 10)
        self.assertEqual(self.message.channelId, 10)
        self.assertEqual(self.message.guildId, 10)
        self.assertEqual(self.message.creationTime, creationTime)
        self.assertTrue(self.message.isDuplicate)

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
                f"Author Id: {self.message.authorId}, Channel Id: {self.message.channelId}, Guild Id: {self.message.guildId}' "
                f"Creation time: {self.message.creationTime}"
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
