import sys
import unittest

from AntiSpam import Guild, User, Message
from AntiSpam.static import Static
from AntiSpam.Exceptions import DuplicateObject, ObjectMismatch


class TestGuild(unittest.TestCase):
    """
    Used to test the ASH object (AntiSpamHandler)
    """

    def test_d(self):
        self.assertEqual(1, 1)
