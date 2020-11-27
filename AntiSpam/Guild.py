"""
LICENSE
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
LICENSE
"""
import discord

from AntiSpam import User
from AntiSpam.Exceptions import ObjectMismatch, DuplicateObject

"""
This is used to maintain a collection of User's in a relevant guild
"""


class Guild:
    """Represents a guild that maintains a collection of User's

    """

    __slots__ = [
        "_id",
        "_bot",
        "_users",
        "_channel",
        "options",
        "logger",
    ]

    def __init__(self, bot, id, options, *, logger):
        """

        Parameters
        ----------
        bot: commands.Bot
            The global bot instance
        id : int
            This guilds id
        """
        self.id = int(id)
        self._bot = bot
        self._users = []
        self.options = options

        self.logger = logger

    def __repr__(self):
        return (
            f"'{self.__class__.__name__} object. Guild id: {self.id}, "
            f"Len Stored Users {len(self._users)}'"
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
        other : Guild
            The object to compare against

        Returns
        -------
        bool
            `True` or `False` depending on whether they are the same or not

        Raises
        ======
        ValueError
            When the comparison object is not of ignore_type `Message`
        """
        if not isinstance(other, Guild):
            raise ValueError("Expected two Guild objects to compare")

        if self.id == other.id:
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
        return hash(self.id)

    def propagate(self, message: discord.Message):
        """
        This method handles a message object and then adds it to
        the relevant member

        Parameters
        ==========
        message : discord.Message
            The message that needs to be propagated out
        """
        if not isinstance(message, discord.Message):
            raise ValueError("Expected message of ignore_type: discord.Message")

        user = User(
            self._bot,
            message.author.id,
            message.guild.id,
            self.options,
            logger=self.logger,
        )
        try:
            user = next(iter(u for u in self._users if u == user))
        except StopIteration:
            self.users = user
            self.logger.info(f"Created User: {user.id}")

        user.propagate(message)

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

        if self.id != value.guild_id:
            raise ObjectMismatch

        for user in self._users:
            if user == value:
                raise DuplicateObject

        self._users.append(value)

    def update_in_guild_state(self, userid):
        """
        
        Gets the userobj and sets the in_guild attribute to False
        as this indicates that the user is no longer in the guild
        ======
        userid
         the id of the user where the state should be updated
        """
        user = User(self._bot, userid, self.id, self.options, logger=self.logger)
        try:
            user = next(iter(u for u in self.users if u == user))
        except StopIteration:
            return  # No need to create a user obj
        user.in_guild = False
