import sys
import unittest

sys.path.insert(0, "..")
# from AntiSpam.Util import Message


class TextMessage(unittest.TestCase):
    """
    Used to test the message object
    """

    def setUp(self):
        """
        Simply setup our message obj before usage
        """
        pass

    def test_pass(self):
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
