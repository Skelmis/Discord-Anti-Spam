"""
This is used to maintain a collection of User's in a relevant guild
"""
import asyncio
import discord

from AntiSpam import User
from AntiSpam.Exceptions import ObjectMismatch, DuplicateObject


class Guild:
    """Represents a guild that maintains a collection of User's

    """

    __slots__ = ["_id", "_bot", "_users", "_channel", "_channelId"]

    def __init__(self, id, channelId, bot):
        """

        Parameters
        ----------
        id : int
            This guilds id
        channelId : int
            This guilds channel to send logs to
        """
        self.id = int(id)
        self._bot = bot
        self._users = []
        self.channel = channelId

        # TODO Add the ability to not set a channel

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

        if self.id == other.id and self._channelId == other._channelId:
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
        return hash((self.id, self._channelId))

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
        if not isinstance(value, int) and not isinstance(value, discord.TextChannel):
            raise ValueError("Expected integer or discord.TextChannel")

        if isinstance(value, int):
            try:
                eventLoop = asyncio.get_event_loop()
                value = await eventLoop.run_until_complete(self.FetchChannel(value))
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
        self._channelId = self._channel.id

    async def FetchChannel(self, channelId):
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

        if self.id != value.guildId:
            raise ObjectMismatch

        for user in self._users:
            if user == value:
                raise DuplicateObject

        self._users.append(value)
