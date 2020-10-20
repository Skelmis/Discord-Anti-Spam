"""
Used to store a user, each of these is relevant per guild rather then globally

Each user object is per guild, rather then globally
"""
import asyncio
from string import Template

import discord

from fuzzywuzzy import fuzz

from AntiSpam import Message
from AntiSpam.Exceptions import DuplicateObject, ObjectMismatch, LogicError
from AntiSpam.static import Static


class User:
    """A class dedicated to maintaining a user, and any relevant messages in a single guild.

    """

    __slots__ = [
        "_id",
        "_guildId",
        "_messages",
        "options",
        "warnCount",
        "kickCount",
        "bot",
        "duplicateCounter",
    ]

    def __init__(self, bot, id, guildId, options):
        """
        Set the relevant information in order to maintain
        and use a per User object for a guild

        Parameters
        ==========
        bot : commands.bot
            Bot instance
        id : int
            The relevant user id
        guildId : int
            The guild (id) this user is belonging to
        options : Dict
            The options we need to check against
        """
        self.id = int(id)
        self.bot = bot
        self.guildId = int(guildId)
        self._messages = []
        self.options = options
        self.warnCount = 0
        self.kickCount = 0
        self.duplicateCounter = 1

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
                raise DuplicateObject

        # No point saving empty messages, although discord shouldnt allow them anyway
        if not bool(message.content and message.content.strip()):
            print("deleting message")
            del message
            return

        relationToOthers = []
        for messageObj in self.messages[::-1]:
            # This calculates the relation to each other
            relationToOthers.append(
                fuzz.token_sort_ratio(message.content, messageObj.content)
            )

        self.messages = message

        # Check if this message is a duplicate of the most recent messages
        for i, proportion in enumerate(relationToOthers):
            if proportion >= self.options["messageDuplicateAccuracy"]:
                """
                The handler works off an internal message duplicate counter 
                so just increment that and then let our logic process it
                """
                self.duplicateCounter += 1
                message.isDuplicate = True
                break  # we don't want to increment to much

        if self.duplicateCounter >= self.options["messageDuplicateCount"]:
            print("Punish time")
            # We need to punish the user with something

            if (
                self.duplicateCounter >= self.options["warnThreshold"]
                and self.warnCount < self.options["kickThreshold"]
                and self.kickCount < self.options["banThreshold"]
            ):
                print("Warn time")
                """
                The user has yet to reach the warn threshold,
                after the warn threshold is reached this will
                then become a kick and so on
                """
                # We are still in the warning area
                # TODO Tell the user if its there final warning before a kick
                channel = value.channel
                message = Template(self.options["warnMessage"]).safe_substitute(
                    {
                        "MENTIONUSER": value.author.mention,
                        "USERNAME": value.author.display_name,
                    }
                )

                asyncio.ensure_future(self.SendToObj(channel, message))
                self.warnCount += 1

            elif (
                self.warnCount >= self.options["kickThreshold"]
                and self.kickCount < self.options["banThreshold"]
            ):
                print("kick time")
                # We should kick the user
                # TODO Tell the user if its there final kick before a ban
                dcChannel = value.channel
                message = Template(self.options["kickMessage"]).safe_substitute(
                    {
                        "MENTIONUSER": value.author.mention,
                        "USERNAME": value.author.display_name,
                    }
                )
                asyncio.ensure_future(
                    self.PunishUser(
                        value.guild,
                        value.author,
                        dcChannel,
                        f"You were kicked from {value.guild.name} for spam.",
                        message,
                        Static.KICK,
                    )
                )
                self.kickCount += 1

            elif self.kickCount >= self.options["banThreshold"]:
                print("ban time")
                # We should ban the user
                dcChannel = value.channel
                message = Template(self.options["banMessage"]).safe_substitute(
                    {
                        "MENTIONUSER": value.author.mention,
                        "USERNAME": value.author.display_name,
                    }
                )
                asyncio.ensure_future(
                    self.PunishUser(
                        value.guild,
                        value.author,
                        dcChannel,
                        f"You were banned from {value.guild.name} for spam.",
                        message,
                        Static.BAN,
                    )
                )
                self.kickCount += 1

            else:
                print("else?")
                raise LogicError

    async def SendToObj(self, messageableObj, message):
        """
        Send a given message to an abc.messageable object

        This does not handle exceptions, they should be handled
        on call as I did not want to overdo this method with
        the required params to notify users.

        Parameters
        ----------
        messageableObj : abc.Messageable
            Where to send message
        message : String
            The message to send

        Raises
        ------
        discord.HTTPException
            Failed to send
        discord.Forbidden
            Lacking permissions to send

        """
        await messageableObj.send(message)

    async def PunishUser(
        self, guild, user, dcChannel, userMessage, guildMessage, method
    ):
        """
        A generic method to handle multiple methods of punishment for a user.

        Currently supports: kicking, banning
        TODO: mutes

        Parameters
        ----------
        guild : discord.Guild
            The guild to punish the user in
        user : discord.User
            The user to punish
        dcChannel : discord.TextChannel
            The channel to send the punishment message to
        userMessage : str
            A message to send to the user who is being punished
        guildMessage : str
            A message to send in the guild for whoever is being punished
        method : str
            A string denoting the type of punishment

        Raises
        ======
        LogicError
            If you do not pass a support punishment method

        """
        if method != Static.KICK and method != Static.BAN:
            raise LogicError(f"{method} is not a recognized punishment method.")

        try:
            try:
                await self.SendToObj(user, userMessage)
            except discord.HTTPException:
                await self.SendToObj(
                    user,
                    f"Sending a message to {user.mention} about their kick failed.",
                )
            finally:
                try:
                    if method == Static.KICK:
                        await guild.kick(
                            user, reason="Automated punishment from DPY Anti-Spam."
                        )
                    elif method == Static.BAN:
                        await guild.ban(
                            user, reason="Automated punishment from DPY Anti-Spam."
                        )
                    else:
                        raise NotImplementedError
                except discord.Forbidden:
                    await self.SendToObj(
                        dcChannel, f"I do not have permission to kick: {user.mention}"
                    )
                except discord.HTTPException:
                    await self.SendToObj(
                        dcChannel,
                        f"An error occurred trying to {method}: {user.mention}",
                    )
                finally:
                    try:
                        await self.SendToObj(dcChannel, guildMessage)
                    except discord.HTTPException:
                        print(
                            f"Failed to send message.\n"
                            f"Guild: {dcChannel.guild.name}({dcChannel.guild.id})\n"
                            f"Channel: {dcChannel.name}({dcChannel.id})"
                        )
        except Exception as e:
            raise e

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

    def GetCorrectDuplicateCount(self):
        """
        Given the internal math has an extra number cos
        accuracy this simply returns the correct value

        Returns
        -------
        self.duplicateCounter - 1
        """
        return self.duplicateCounter - 1
