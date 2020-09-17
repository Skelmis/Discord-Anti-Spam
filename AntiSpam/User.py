"""
Used to store a user, each of these is relevant per guild rather then globally

Each user object is per guild, rather then globally
"""
from AntiSpam import Message
from AntiSpam.Exceptions import DuplicateMessage


class User:
    def __init__(self, id):
        """
        Set the relevant information in order to maintain
        and use a per User object for a guild

        Parameters
        ==========
        id : int
            The relevant user id
        """
        self.id = int(id)
        self._messages = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._id = value

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        if not isinstance(value, Message):
            raise ValueError("Expected Message object")

        for message in self._messages:
            if message == value:
                raise DuplicateMessage

        self._messages.append(value)
