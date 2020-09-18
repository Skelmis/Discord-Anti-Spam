"""
Used to store a user, each of these is relevant per guild rather then globally

Each user object is per guild, rather then globally
"""
import discord

from AntiSpam import Message
from AntiSpam.Exceptions import DuplicateObject, ObjectMismatch


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

    def __repr__(self):
        return (
            f"{self.__class__.__name__} object. User id: {self.id}, Guild id: {self.guildId}, "
            f"Len Stored Message {len(self._messages)}"
        )

    def __str__(self):
        return f"{self.__class__.__name__} object for {self.id}."

    def __eq__(self, other):
        """
        This is called with a 'obj1 == obj2' comparison object is made

        Checks against stored id's to figure out if they are
        representing the same User or not

        Parameters
        ----------
        other : User
            The object to compare against

        Returns
        -------
        bool
            `True` or `False` depending on whether they are the same or not

        Raises
        ======
        ValueError
            When the comparison object is not of type `Message`
        """
        if not isinstance(other, User):
            raise ValueError("Expected two User objects to compare")

        if self.id == other.id and self.guildId == other.guildId:
            return True
        return False

    def __hash__(self):
        """
        Given we create a __eq__ dunder method, we also needed
        to create one for __hash__ lol

        Returns
        -------
        int
            The hash of all id's
        """
        return hash((self.id, self.guildId))

    def propagate(self, value: discord.Message):
        """
        This method handles a message object and then adds it to
        the relevant user

        Parameters
        ==========
        value : discord.Message
            The message that needs to be propagated out
        """
        if not isinstance(value, discord.Message):
            raise ValueError("Expected message of type: discord.Message")

        message = Message(
            value.id,
            value.clean_content,
            value.author.id,
            value.channel.id,
            value.guild.id,
        )
        for messageObj in self.messages:
            if message == messageObj:
                messageObj.propagate(message)
                return

        self.messages = message
        print(self.messages)

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
        DuplicateObject
            It won't maintain two message objects with the same
            id's, and it will complain about it haha
        """
        if not isinstance(value, Message):
            raise ValueError("Expected Message object")

        if value.authorId != self.id or value.guildId != self.guildId:
            raise ObjectMismatch

        for message in self._messages:
            if message == value:
                raise DuplicateObject

        self._messages.append(value)
