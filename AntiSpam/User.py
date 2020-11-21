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
import logging
import asyncio
import datetime
from copy import deepcopy
from string import Template

import discord

from fuzzywuzzy import fuzz

from AntiSpam import Message
from AntiSpam.Exceptions import (
    DuplicateObject,
    ObjectMismatch,
    LogicError,
    MissingGuildPermissions,
)
from AntiSpam.static import Static
from AntiSpam.Util import embed_to_string


class User:
    """A class dedicated to maintaining a user, and any relevant messages in a single guild.

    """

    __slots__ = [
        "_id",
        "_guild_id",
        "_messages",
        "options",
        "warn_count",
        "kick_count",
        "bot",
        "inGuild",
        "duplicate_counter",
        "logger",
    ]

    def __init__(self, bot, id, guild_id, options, *, logger):
        """
        Set the relevant information in order to maintain
        and use a per User object for a guild

        Parameters
        ==========
        bot : commands.bot
            Bot instance
        id : int
            The relevant user id
        guild_id : int
            The guild (id) this user is belonging to
        options : Dict
            The options we need to check against
        """
        self.id = int(id)
        self.bot = bot
        self.guild_id = int(guild_id)
        self._messages = []
        self.options = options
        self.inGuild = True  # Indicates if a user is in the guild or not 
        self.warn_count = 0
        self.kick_count = 0
        self.duplicate_counter = 1
        self.logger = logger

    def __repr__(self):
        return (
            f"'{self.__class__.__name__} object. User id: {self.id}, Guild id: {self.guild_id}, "
            f"Len Stored Messages {len(self._messages)}'"
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
            When the comparison object is not of ignore_type `Message`
        """
        if not isinstance(other, User):
            raise ValueError("Expected two User objects to compare")

        if self.id == other.id and self.guild_id == other.guild_id:
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
        return hash((self.id, self.guild_id))

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
            raise ValueError("Expected message of ignore_type: discord.Message")
         
        # Here we just check if the user is still in the guild by checking if the inGuild attribute is False.
        # Because if its False then we don't need to process the message.
        if not self.inGuild:
            return
        
        self.clean_up(datetime.datetime.now(datetime.timezone.utc))

        # No point saving empty messages, although discord shouldn't allow them anyway
        if not bool(value.content and value.content.strip()):
            if not value.embeds:
                return

            else:
                embed = value.embeds[0]
                if not isinstance(embed, discord.Embed):
                    return

                if embed.type.lower() != "rich":
                    return

                content = embed_to_string(embed)

                message = Message(
                    value.id,
                    content,
                    value.author.id,
                    value.channel.id,
                    value.guild.id,
                )

        else:
            message = Message(
                value.id,
                value.clean_content,
                value.author.id,
                value.channel.id,
                value.guild.id,
            )

        # TODO Figure out a nice way to implement an iter() on this
        for message_obj in self.messages:
            if message == message_obj:
                raise DuplicateObject

        relation_to_others = []
        for message_obj in self.messages[::-1]:
            # This calculates the relation to each other
            relation_to_others.append(
                fuzz.token_sort_ratio(message.content, message_obj.content)
            )

        self.messages = message
        self.logger.info(f"Created Message: {message.id}")

        # Check if this message is a duplicate of the most recent messages
        for i, proportion in enumerate(relation_to_others):
            if proportion >= self.options["message_duplicate_accuracy"]:
                """
                The handler works off an internal message duplicate counter 
                so just increment that and then let our logic process it
                """
                self.duplicate_counter += 1
                message.is_duplicate = True
                break  # we don't want to increment to much

        if self.duplicate_counter >= self.options["message_duplicate_count"]:
            self.logger.debug(
                f"Message: ({message.id}) requires some form of punishment"
            )
            # We need to punish the user with something

            if (
                self.duplicate_counter >= self.options["warn_threshold"]
                and self.warn_count < self.options["kick_threshold"]
                and self.kick_count < self.options["ban_threshold"]
            ):
                self.logger.debug(f"Attempting to warn: {message.author_id}")
                """
                The user has yet to reach the warn threshold,
                after the warn threshold is reached this will
                then become a kick and so on
                """
                # We are still in the warning area
                # TODO Tell the user if its there final warning before a kick
                channel = value.channel
                message = Template(self.options["warn_message"]).safe_substitute(
                    {
                        "MENTIONUSER": value.author.mention,
                        "USERNAME": value.author.display_name,
                    }
                )

                asyncio.ensure_future(self._send_to_obj(channel, message))
                self.warn_count += 1

            elif (
                self.warn_count >= self.options["kick_threshold"]
                and self.kick_count < self.options["ban_threshold"]
            ):
                self.logger.debug(f"Attempting to kick: {message.author_id}")
                # We should kick the user
                # TODO Tell the user if its there final kick before a ban
                dc_channel = value.channel
                message = Template(self.options["kick_message"]).safe_substitute(
                    {
                        "MENTIONUSER": value.author.mention,
                        "USERNAME": value.author.display_name,
                    }
                )
                asyncio.ensure_future(
                    self._punish_user(
                        value.guild,
                        value.author,
                        dc_channel,
                        f"You were kicked from {value.guild.name} for spam.",
                        message,
                        Static.KICK,
                    )
                )
                self.kick_count += 1

            elif self.kick_count >= self.options["ban_threshold"]:
                self.logger.debug(f"Attempting to ban: {message.author_id}")
                # We should ban the user
                dc_channel = value.channel
                message = Template(self.options["ban_message"]).safe_substitute(
                    {
                        "MENTIONUSER": value.author.mention,
                        "USERNAME": value.author.display_name,
                    }
                )
                asyncio.ensure_future(
                    self._punish_user(
                        value.guild,
                        value.author,
                        dc_channel,
                        f"You were banned from {value.guild.name} for spam.",
                        message,
                        Static.BAN,
                    )
                )
                self.kick_count += 1

            else:
                raise LogicError

    async def _send_to_obj(self, messageable_obj, message):
        """
        Send a given message to an abc.messageable object

        This does not handle exceptions, they should be handled
        on call as I did not want to overdo this method with
        the required params to notify users.

        Parameters
        ----------
        messageable_obj : abc.Messageable
            Where to send message
        message : String
            The message to send

        Raises
        ------
        discord.HTTPException
            Failed to send
        discord.Forbidden
            Lacking permissions to send

        Returns
        =======
        discord.Message
            The sent messages object

        """
        return await messageable_obj.send(message)

    async def _punish_user(
        self, guild, user, dc_channel, user_message, guild_message, method
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
        dc_channel : discord.TextChannel
            The channel to send the punishment message to
        user_message : str
            A message to send to the user who is being punished
        guild_message : str
            A message to send in the guild for whoever is being punished
        method : str
            A string denoting the ignore_type of punishment

        Raises
        ======
        LogicError
            If you do not pass a support punishment method

        """
        if method != Static.KICK and method != Static.BAN:
            raise LogicError(f"{method} is not a recognized punishment method.")

        perms = guild.me.guild_permissions  # TODO Test this
        if not perms.kick_members:
            raise MissingGuildPermissions(
                f"I need kick perms to punish someone in {guild.name}"
            )
        elif not perms.ban_members:
            raise MissingGuildPermissions(
                f"I need ban perms to punish someone in {guild.name}"
            )

        m = None

        try:
            # Attempt to message the punished user, about their punishment
            try:
                m = await self._send_to_obj(user, user_message)
            except discord.HTTPException:
                await self._send_to_obj(
                    dc_channel,
                    f"Sending a message to {user.mention} about their {method} failed.",
                )
                self.logger.warn(f"Failed to message User: ({user.id}) about {method}")
            finally:

                # Even if we can't tell them they are being punished
                # We still need to punish them, so try that
                try:
                    if method == Static.KICK:
                        await guild.kick(
                            user, reason="Automated punishment from DPY Anti-Spam."
                        )
                        self.logger.info(f"Kicked User: ({user.id})")
                    elif method == Static.BAN:
                        await guild.ban(
                            user, reason="Automated punishment from DPY Anti-Spam."
                        )
                        self.logger.info(f"Banned User: ({user.id})")
                    else:
                        raise NotImplementedError
                except discord.Forbidden:
                    await self._send_to_obj(
                        dc_channel, f"I do not have permission to kick: {user.mention}"
                    )
                    self.logger.warn(f"Required Permissions are missing for: {method}")
                    if m is not None:
                        await self._send_to_obj(
                            user,
                            "I failed to punish you because I lack permissions, but still you shouldn't do it.",
                        )

                except discord.HTTPException:
                    await self._send_to_obj(
                        dc_channel,
                        f"An error occurred trying to {method}: {user.mention}",
                    )
                    self.logger.warn(f"An error occurred trying to {method}: {user.id}")
                    if m is not None:
                        await self._send_to_obj(
                            user,
                            "I failed to punish you because I lack permissions, but still you shouldn't do it.",
                        )

                else:
                    try:
                        await self._send_to_obj(dc_channel, guild_message)
                    except discord.HTTPException:
                        self.logger.error(
                            f"Failed to send message.\n"
                            f"Guild: {dc_channel.guild.name}({dc_channel.guild.id})\n"
                            f"Channel: {dc_channel.name}({dc_channel.id})"
                        )
        except Exception as e:
            raise e

    def get_correct_duplicate_count(self):
        """
        Given the internal math has an extra number cos
        accuracy this simply returns the correct value

        Returns
        -------
        self.duplicate_counter - 1
        """
        return self.duplicate_counter - 1

    def clean_up(self, currentTime):
        """
        This logic works around checking the current
        time vs a messages creation time. If the message
        is older by the config amount it can be cleaned up
        """
        self.logger.debug("Attempting to remove outdated Message's")

        def _is_still_valid(message):
            """
            Given a message, figure out if it hasnt
            expired yet based on timestamps
            """
            difference = currentTime - message.creationTime
            offset = datetime.timedelta(
                milliseconds=self.options.get("message_interval")
            )

            if difference >= offset:
                return False
            return True

        currentMessages = []
        outstandingMessages = []

        for message in self._messages:
            if _is_still_valid(message):
                currentMessages.append(message)
            else:
                outstandingMessages.append(message)

        self._messages = deepcopy(currentMessages)

        # Now if we have outstanding messages we need
        # to process them and see if we need to deincrement
        # the duplicate counter as we are removing them from
        # the queue otherwise everything stacks up
        for outstandingMessage in outstandingMessages:
            if outstandingMessage.is_duplicate:
                self.duplicate_counter -= 1
                self.logger.debug(
                    f"Removing duplicate Message: {outstandingMessage.id}"
                )
            elif self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Removing Message: {outstandingMessage.id}")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._id = value

    @property
    def guild_id(self):
        return self._guild_id

    @guild_id.setter
    def guild_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._guild_id = value

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

        if value.author_id != self.id or value.guild_id != self.guild_id:
            raise ObjectMismatch

        for message in self._messages:
            if message == value:
                raise DuplicateObject

        self._messages.append(value)
