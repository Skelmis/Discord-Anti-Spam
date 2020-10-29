import sys
import unittest


from AntiSpam.Exceptions import *


class TestUser(unittest.TestCase):
    """
    Used to test the Exceptions
    """

    def test_baseException(self):
        self.assertEqual(
            "A base exception handler for the ASH ecosystem.", str(BaseASHException())
        )

    def test_DuplicateObject(self):
        self.assertEqual(
            "Raised because you attempted to create an object, using the exact same id's as a pre-existing one.",
            str(DuplicateObject()),
        )

    def test_ObjectMismatch(self):
        self.assertEqual(
            "Raised because you attempted add a message to a user, but that user didn't create that message.",
            str(ObjectMismatch()),
        )

    def test_LogicError(self):
        self.assertEqual(
            "Raised because internal logic has failed. Please create an issue in the github.",
            str(LogicError()),
        )

    def test_MessageAssignment(self):
        err = BaseASHException("A message")
        self.assertEqual("A message", str(err))
