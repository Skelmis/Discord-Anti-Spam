"""
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
"""

"""
This is used to maintain a collection of User's in a relevant guild
"""
import asyncio
import discord

from AntiSpam import User
from AntiSpam.Exceptions import ObjectMismatch, DuplicateObject
from AntiSpam.static import Static


class Guild:
    """Represents a guild that maintains a collection of User's

    """

    __slots__ = [
        "_id",
        "_bot",
        "_users",
        "_channel",
        "_channel_id",
        "options",
        "logger",
    ]

    def __init__(self, bot, id, options, channel_id=None, *, logger):
        """

        Parameters
        ----------
        bot: commands.Bot
            The global bot instance
        id : int
            This guilds id
        channel_id : int
            This guilds channel to send logs to
        """
        self.id = int(id)
        self._bot = bot
        self._users = []
        self.options = options
        self.channel = channel_id

        self.logger = logger

        # TODO Add the ability to not set a channel

    def __repr__(self):
        return (
            f"'{self.__class__.__name__} object. Guild id: {self.id}, "
            f"Len Stored Users {len(self._users)}, Log Channel Id: {self.channel}'"
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
            When the comparison object is not of type `Message`
        """
        if not isinstance(other, Guild):
            raise ValueError("Expected two Guild objects to compare")

        if self.id == other.id and self._channel_id == other._channel_id:
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
        return hash((self.id, self._channel_id))

    def propagate(self, message: discord.Message):
        """
        This method handles a message object and then adds it to
        the relevant user

        Parameters
        ==========
        message : discord.Message
            The message that needs to be propagated out
        """
        if not isinstance(message, discord.Message):
            raise ValueError("Expected message of type: discord.Message")

        if isinstance(self._channel, int):
            self.channel = message.channel

        user = User(
            self._bot,
            message.author.id,
            message.guild.id,
            self.options,
            logger=self.logger,
        )
        for userObj in self.users:
            if user == userObj:
                return userObj.propagate(message)

        self.users = user
        self.logger.info(f"Created User: {user.id}")

        user.propagate(message)

        # TODO Cleanup after a user is banned

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._id = value

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if value is None:
            self._channel = value
            self._channel_id = value
            return

        if not isinstance(value, int) and not isinstance(value, discord.TextChannel):
            raise ValueError("Expected integer or discord.TextChannel")

        if isinstance(value, int):
            try:
                eventLoop = asyncio.get_event_loop()
                value = eventLoop.run_until_complete(self.fetch_channel(value))
            except discord.InvalidData:
                raise ValueError("An unknown channel type was received from Discord.")
            except discord.NotFound:
                raise ValueError("Invalid Channel ID.")
            except discord.Forbidden:
                raise ValueError("You do not have permission to fetch this channel.")
            except discord.HTTPException:
                raise ValueError("Retrieving the channel failed.")
            except Exception as e:
                raise e

        self._channel = value
        self._channel_id = self._channel.id

    async def fetch_channel(self, channelId):
        return await self._bot.fetch_channel(channelId)

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
