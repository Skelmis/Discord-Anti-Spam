"""
LICENSE
The MIT License (MIT)

Copyright (c) 2020-2021 Skelmis

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
import datetime
import logging
from copy import deepcopy
from unittest.mock import MagicMock

import discord

from . import AntiSpamHandler
from .Exceptions import UserNotFound


class AntiSpamTracker:
    """
    A class devoted to people who want to handle punishments themselves.

    This class wraps a few things, and handles the logic of ensuring
    everything exists (or doesnt) among other things such as
    untracking users after the valid storage interval expires

    In order to use
    this in your code, you can either:\n
     - Subclass this class and override the ``do_punishment`` method and then use it that way to keep it clean
     - Initialize this class and simply use the bool ``is_spamming()`` and do punishments based off that
     - Initialize this class and simply use ``get_user_count()`` to get the number of times the user should be punished and do your own logic

    *This mainly just depends on how granular you want to be within your code base.*

    The way it works, is everytime you call ``propagate`` you simply pass the returned
    data into `update_cache` and it will update said Members cache if AntiSpamHandler
    thinks that they should be punished. Now, you set ``spam_amount_to_punish``
    when creating an instance of this class and that is used to check if YOU
    think they should be punished, and what punishment to give when they hit that cap.

    **Basically:**\n
    ``propagate`` -> ``update_cache``, if the User should be punished we increment internal counter

    ``is_spamming`` -> Checks if the User's internal counter meets ``spam_amount_to_punish`` and returns a bool

    Notes
    =====
    This Class recognizes that individual guilds can have different options
    and will attempt to work with said options to the best of its ability.
    This is lazily conducted however, so if you wish to use any of the methods
    listed below please call them on this class rather then on your base
    AntiSpamHandler. (They will also update the AntiSpamHandler dont worry)

    - ``add_custom_guild_options``
    - ``remove_custom_guild_options``
    """

    __slots__ = [
        "user_tracking",
        "valid_global_interval",
        "anti_spam_handler",
        "punish_min_amount",
    ]

    def __init__(
        self,
        anti_spam_handler: AntiSpamHandler,
        spam_amount_to_punish,
        valid_timestamp_interval=None,
    ) -> None:
        """
        Initialize this class and get it ready for usage.

        Parameters
        ----------
        anti_spam_handler : AntiSpamHandler
            Your AntiSpamHandler instance
        spam_amount_to_punish : int
            A number denoting the minimum value required
            per user in order trip `is_spamming`

            **NOTE this is in milliseconds**
        valid_timestamp_interval : int
            How long a timestamp should remain 'valid' for.
            Defaults to ``AntiSpamHandler.options.get("message_interval")``

        Raises
        ------
        TypeError
            Invalid Arg Type
        ValueError
            Invalid Arg Type
        """
        self.punish_min_amount = int(spam_amount_to_punish)

        if not isinstance(anti_spam_handler, AntiSpamHandler):
            raise TypeError("Expected anti_spam_handler of type AntiSpamHandler")

        self.anti_spam_handler = anti_spam_handler

        if valid_timestamp_interval is not None:
            if isinstance(valid_timestamp_interval, (str, float)):
                valid_timestamp_interval = int(valid_timestamp_interval)
            elif isinstance(valid_timestamp_interval, int):
                pass
            else:
                raise TypeError("Expected valid_timestamp_interval of type int")

        self.valid_global_interval = (
            valid_timestamp_interval
            or anti_spam_handler.options.get("message_interval")
        )
        self.valid_global_interval = int(self.valid_global_interval)

        self.user_tracking = {}

        logging.info("AntiSpamTracker is initialized and ready to go")

    def __str__(self):
        guilds = len(self.user_tracking)
        users = 0
        for guild in self.user_tracking.values():
            users += len(guild)

        return_value = f"AntiSpamTracker(AntiSpamHandler Instance, {self.punish_min_amount}, {self.valid_global_interval})"
        return_value += f"\nGuilds: {guilds} | Users (Non Unique): {users}"
        return return_value

    def __repr__(self):
        return_value = f"AntiSpamTracker(AntiSpamHandler Instance, {self.punish_min_amount}, {self.valid_global_interval})\n"
        return_value += str(self.user_tracking)
        return return_value

    def update_cache(self, message: discord.Message, data: dict) -> None:
        """
        Takes the data returned from `propagate`
        and updates this Class's internal cache

        Parameters
        ----------
        message : discord.Message
            The message related to `data's` propagation
        data : dict
            The data returned from `propagate`
        """
        if not isinstance(message, (discord.Message, MagicMock)):
            raise TypeError("Expected message of type: discord.Message")

        if not isinstance(data, dict):
            raise TypeError("Expected data of type: dict")

        if not message.guild:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        if not data.get("should_be_punished_this_message"):
            # They shouldn't be punished so don't increase cache
            return

        # We now need to increase there cache
        if guild_id not in self.user_tracking:
            self.user_tracking[guild_id] = {}

        if user_id not in self.user_tracking[guild_id]:
            self.user_tracking[guild_id][user_id] = []

        self.user_tracking[guild_id][user_id].append(timestamp)
        logging.debug(f"Cache updated for user ({user_id}) in guild ({guild_id})")

    def get_user_count(self, message: discord.Message) -> int:
        """
        Returns how many messages that are still 'valid'
        (counted as spam) a certain user has

        Parameters
        ----------
        message : discord.Message
            The message from which to extract user

        Returns
        -------
        int
            How many times this user has sent a
            message that has been marked as
            'punishment worthy' by AntiSpamHandler
            within the valid interval time period

        Raises
        ------
        UserNotFound
            The User for the ``message`` could not be found

        """
        if not isinstance(message, (discord.Message, MagicMock)):
            raise TypeError("Expected message of type: discord.Message")

        user_id = message.author.id
        guild_id = message.guild.id

        if guild_id not in self.user_tracking:
            raise UserNotFound

        if user_id not in self.user_tracking[guild_id]:
            raise UserNotFound

        self.remove_outdated_timestamps(guild_id=guild_id, user_id=user_id)

        return len(self.user_tracking[guild_id][user_id])

    def remove_outdated_timestamps(self, guild_id, user_id):
        """
        This logic works around checking the current
        time vs a messages creation time. If the message
        is older by the config amount it can be cleaned up

        *Generally not called by the end user*

        Parameters
        ==========
        guild_id : int
            The guild's id to clean
        user_id : int
            The id of the user to clean up

        """
        logging.debug("Attempting to remove outdated timestamp's")
        current_time = datetime.datetime.now(datetime.timezone.utc)

        def _is_still_valid(timestamp):
            """
            Given a timestamp, figure out if it hasn't
            expired yet
            """
            difference = current_time - timestamp
            offset = datetime.timedelta(
                milliseconds=self._get_guild_valid_interval(guild_id=guild_id)
            )

            if difference >= offset:
                return False
            return True

        current_timestamps = []

        for timestamp in self.user_tracking[guild_id][user_id]:
            if _is_still_valid(timestamp):
                current_timestamps.append(timestamp)

        logging.debug(
            f"Removed {len(self.user_tracking[guild_id][user_id]) - len(current_timestamps)} 'timestamps'"
        )

        self.user_tracking[guild_id][user_id] = deepcopy(current_timestamps)

    def remove_punishments(self, message: discord.Message):
        """
        After you punish someone, call this method
        to 'clean up' there punishments.
        
        Parameters
        ----------
        message : discord.Message
            The message to extract user from

        Raises
        ------
        TypeError
            Invalid arg

        Notes
        -----
        If the user can't be found in cache,
        it executes the same as if the user
        could be found in cache for what should
        be somewhat obvious reasons. (They shouldn't
        exist after this method finishes)
        """
        if not isinstance(message, (discord.Message, MagicMock)):
            raise TypeError("Expected message of type: discord.Message")

        user_id = message.author.id
        guild_id = message.guild.id

        if guild_id not in self.user_tracking:
            return

        if user_id not in self.user_tracking[guild_id]:
            return

        self.user_tracking[guild_id].pop(user_id)

    def clean_cache(self) -> None:
        """
        Cleans the entire internal cache
        removing any empty users, and empty
        guilds by extension

        Notes
        -----
        This is more part of the Optimising Package Usage section,
        run this once a week/day or somethin depending on how big
        your bot is. I haven't profiled things.
        """
        for guild_id, guild in deepcopy(self.user_tracking).items():
            for user_id, user in deepcopy(guild).items():
                self.remove_outdated_timestamps(guild_id=guild_id, user_id=user_id)

                if len(self.user_tracking[guild_id][user_id]) == 0:
                    self.user_tracking[guild_id].pop(user_id)

            if not bool(self.user_tracking[guild_id]):
                self.user_tracking.pop(guild_id)

        logging.debug("Successfully cleaned the cache")

    def _get_guild_valid_interval(self, guild_id):
        """
        Returns the correct ``valid_global_interval``
        except on a per guild level taking into account
        custom guild options

        Parameters
        ----------
        guild_id

        Returns
        -------
        int
            The correct interval time

        Notes
        -----
        Silently ignores if a guild doesnt exist.
        There is a global default for a reason.
        """
        if guild_id not in self.user_tracking:
            return self.valid_global_interval

        if "valid_interval" not in self.user_tracking[guild_id]:
            return self.valid_global_interval

        return self.user_tracking[guild_id]["valid_interval"]

    def is_spamming(self, message: discord.Message) -> bool:
        """
        Given a message, deduce and return if a user
        is classed as 'spamming' or not based on ``punish_min_amount``

        Parameters
        ----------
        message : discord.Messsage
            The message to extract guild and user from

        Returns
        -------
        bool
            True if the User is spamming else False

        """
        if not isinstance(message, (discord.Message, MagicMock)):
            raise TypeError("Expected message of type: discord.Message")

        try:
            user_count = self.get_user_count(message=message)
            if user_count >= self.punish_min_amount:
                return True
        except UserNotFound:
            return False
        else:
            return False

    async def do_punishment(self, message: discord.Message, *args, **kwargs) -> None:
        """
        This only exists for if the user wishes to subclass
        this class and implement there own logic for punishments
        here.

        Parameters
        ----------
        message : discord.Message
            The message to extract the guild and user from

        Notes
        -----
        This does nothing unless you subclass
        and implement it yourself.

        """
        pass

    # <!-- Stuff I take over from AntiSpamHandler -->
    def add_custom_guild_options(self, guild_id: int, **kwargs):
        """
        To see how to use this, refer to ``AntiSpam.AntiSpamHandler.AntiSpamHandler.add_custom_guild_options``

        See Also
        --------
        AntiSpam.AntiSpamHandler.AntiSpamHandler.add_custom_guild_options :
            The method that this calls under the hood

        Notes
        -----
        Not unit-tested, I just assume it works
        since ``add_custom_guild_options`` is unit-tested.
        If this doesnt work as intended, please open
        an issue.

        """
        if kwargs.get("message_interval"):
            if guild_id not in self.user_tracking:
                self.user_tracking[guild_id] = {}

            self.user_tracking[guild_id]["valid_interval"] = kwargs.get(
                "message_interval"
            )
            logging.debug(f"Set custom 'valid_interval' for guild: {guild_id}")

        self.anti_spam_handler.add_custom_guild_options(guild_id=guild_id, **kwargs)

        logging.debug("Did method 'add_custom_guild_options'")

    def remove_custom_guild_options(self, guild_id: int):
        """
        To see how to use this, refer to ``AntiSpam.AntiSpamHandler.AntiSpamHandler.remove_custom_guild_options``

        See Also
        --------
        AntiSpam.AntiSpamHandler.AntiSpamHandler.remove_custom_guild_options :
            The method that this calls under the hood

        Notes
        -----
        Not unit-tested, I just assume it works
        since ``add_custom_guild_options`` is unit-tested.
        If this doesnt work as intended, please open
        an issue.

        """
        if guild_id in self.user_tracking:
            if "valid_interval" in self.user_tracking[guild_id]:
                self.user_tracking[guild_id].pop("valid_interval")
                logging.debug(f"Removed custom 'valid_interval' for guild: {guild_id}")

        self.anti_spam_handler.add_custom_guild_options(guild_id=guild_id)

        logging.debug("Did method 'remove_custom_guild_options'")
