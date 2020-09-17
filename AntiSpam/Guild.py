"""
This is used to maintain a collection of User's in a relevant guild
"""


class Guild:
    """Represents a guild that maintains a collection of User's

    """

    __slots__ = ["_id"]

    def __init__(self, id):
        """

        Parameters
        ----------
        id : int
            This guilds id
        """
        self.id = int(id)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._id = value
