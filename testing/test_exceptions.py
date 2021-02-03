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
            "Raised because you attempted to create and add an object, using the exact same id's as a pre-existing one.",
            str(DuplicateObject()),
        )

    def test_ObjectMismatch(self):
        self.assertEqual(
            "Raised because you attempted add a message to a member, but that member didn't create that message.",
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
