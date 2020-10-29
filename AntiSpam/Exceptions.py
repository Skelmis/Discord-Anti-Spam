"""
A file devoted to some nice custom exceptions of mine
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
    """Raised because you attempted to create an object, using the exact same id's as a pre-existing one."""


class ObjectMismatch(BaseASHException):
    """Raised because you attempted add a message to a user, but that user didn't create that message."""


class LogicError(BaseASHException):
    """Raised because internal logic has failed. Please create an issue in the github."""
