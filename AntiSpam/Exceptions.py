"""
A file devoted to some nice custom exceptions of mine
"""


class DuplicateMessage(Exception):
    """Raised because you attempted to create a message object, using the exact same id's."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self):
        return self.message
