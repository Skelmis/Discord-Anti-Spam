import sys
import unittest

sys.path.insert(0, "..")
from AntiSpam import Guild, User, Message


class TestGuild(unittest.TestCase):
    """
    Used to test the Guild object
    """
