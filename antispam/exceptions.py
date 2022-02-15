"""
The MIT License (MIT)

Copyright (c) 2020-Current Skelmis

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


class BaseASHException(Exception):
    """A base exception handler for the ASH ecosystem."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self):
        return self.message


class PropagateFailure(BaseASHException):
    def __init__(self, *args, data: dict):
        super().__init__(args)
        self.data = data


class InvocationCancelled(BaseASHException):
    """Called when a pre-invoke plugin returned `cancel_next_invocation`"""


class UnsupportedAction(BaseASHException):
    """The attempt action is unsupported."""


class DuplicateObject(BaseASHException):
    """Raised because you attempted to create and add an object, using the exact same id's as a pre-existing one."""


class ObjectMismatch(BaseASHException):
    """Raised because you attempted add a message to a member, but that member didn't create that message."""


class InvalidMessage(BaseASHException):
    """Could not create a use-able message for the given message."""


class LogicError(BaseASHException):
    """Raised because internal logic has failed. Please create an issue in the github and include traceback."""


class MissingGuildPermissions(BaseASHException):
    """I need both permissions to kick & ban people from this guild in order to work!"""


class NotFound(BaseASHException):
    """Something could not be found."""


class MemberNotFound(NotFound):
    """A Member matching this id and guild id could not be found in the cache."""


class MemberAddonNotFound(NotFound):
    """This class has no addon stored on this member."""


class GuildNotFound(NotFound):
    """A Guild matching this guild id could not be found in the cache."""


class GuildAddonNotFound(GuildNotFound):
    """This class has not addon stored on this guild."""


class PluginError(BaseASHException):
    """An error occurred that was related to a plugin and not AntiSpamHandler"""


class ExistingEntry(BaseASHException):
    """An entry was already found in the timed cache with this key."""


class NonExistentEntry(BaseASHException):
    """No entry found in the timed cache with this key."""
