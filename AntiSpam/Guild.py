"""
This is used to maintain a collection of User's in a relevant guild
"""
from AntiSpam import User
from AntiSpam.Exceptions import ObjectMismatch, DuplicateObject


class Guild:
    """Represents a guild that maintains a collection of User's

    """

    __slots__ = ["_id", "_users", "_channel"]

    def __init__(self, id):
        """

        Parameters
        ----------
        id : int
            This guilds id
        """
        self.id = int(id)
        self.channel = channel
        self._users = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._id = value

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, value):
        """
        Raises
        ======
        DuplicateObject
            It won't maintain two message objects with the same
            id's, and it will complain about it haha
        ObjectMismatch
            Raised if `value` wasn't made by this person, so they
            shouldn't be the ones maintaining the reference
        """
        if not isinstance(value, User):
            raise ValueError("Expected User object")

        if self.id != value.guildId:
            raise ObjectMismatch

        for user in self._users:
            if user == value:
                raise DuplicateObject

        self._users.append(value)
