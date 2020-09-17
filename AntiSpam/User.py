"""
Used to store a user, each of these is relevant per guild rather then globally

Each user object is per guild, rather then globally
"""
from AntiSpam import Message
from AntiSpam.Exceptions import DuplicateMessage, ObjectMismatch


class User:
    """A class dedicated to maintaining a user, and any relevant messages in a single guild.

    """

    __slots__ = ["_id", "_guildId", "_messages"]

    def __init__(self, id, guildId):
        """
        Set the relevant information in order to maintain
        and use a per User object for a guild

        Parameters
        ==========
        id : int
            The relevant user id
        guildId : int
            The guild (id) this user is belonging to
        """
        self.id = int(id)
        self.guildId = int(guildId)
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
    def guildId(self):
        return self._guildId

    @guildId.setter
    def guildId(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._guildId = value

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        """
        Raises
        ======
        DuplicateMessage
            It won't maintain two message objects with the same
            id's, and it will complain about it haha
        """
        if not isinstance(value, Message):
            raise ValueError("Expected Message object")

        if value.authorId != self.id or value.guildId != self.guildId:
            raise ObjectMismatch

        for message in self._messages:
            if message == value:
                raise DuplicateMessage

        self._messages.append(value)
