"""
LICENSE
The MIT License (MIT)

Copyright (c) 2020-2021 Skelmis

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
LICENSE
"""


class BaseASHException(Exception):
    """A base exception handler for the ASH ecosystem."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self):
        return self.message


class DuplicateObject(BaseASHException):
    """Raised because you attempted to create and add an object, using the exact same id's as a pre-existing one."""


class ObjectMismatch(BaseASHException):
    """Raised because you attempted add a message to a member, but that member didn't create that message."""


class LogicError(BaseASHException):
    """Raised because internal logic has failed. Please create an issue in the github."""


class MissingGuildPermissions(BaseASHException):
    """I need both permissions to kick & ban people from this guild in order to work!"""


class UserNotFound(BaseASHException):
    """A User matching this id and guild id could not be found in the cache."""


class ExtensionError(BaseASHException):
    """An error occurred that was related to an extension and not AntiSpamHandler"""
