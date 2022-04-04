"""
The MIT License (MIT)

Copyright (c) 2020-Current Skelmis

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
import datetime
import logging
import typing

from antispam import AntiSpamHandler
from antispam.abc import Lib
from antispam.base_plugin import BasePlugin
from antispam.dataclasses import CorePayload, Member
from antispam.exceptions import (
    GuildAddonNotFound,
    GuildNotFound,
    MemberAddonNotFound,
    MemberNotFound,
)
from antispam.plugin_cache import PluginCache
from antispam.util import get_aware_time

log = logging.getLogger(__name__)


class AntiSpamTracker(BasePlugin):
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

    Attributes
    ----------
    member_tracking: PluginCache
        The underlying cache mechanism for data storage
    """

    __slots__ = [
        "member_tracking",
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
            per member in order trip `is_spamming`
        valid_timestamp_interval : int
            How long a timestamp should remain 'valid' for.
            Defaults to ``AntiSpamHandler.options.get("message_interval")``

            **NOTE this is in milliseconds**

        Raises
        ------
        TypeError
            Invalid Arg Type
        ValueError
            Invalid Arg Type
        """
        super().__init__(is_pre_invoke=False)

        try:
            self.punish_min_amount = int(spam_amount_to_punish)
        except (TypeError, ValueError):
            raise ValueError(
                "Expected `spam_amount_to_punish` of type int or int convertable"
            ) from None

        if not isinstance(anti_spam_handler, AntiSpamHandler):
            raise TypeError("Expected anti_spam_handler of type AntiSpamHandler")

        if not anti_spam_handler.options.no_punish:
            log.warning("`no_punish` is not enabled! This will likely lead to issues")

        self.anti_spam_handler: AntiSpamHandler = anti_spam_handler
        self.lib_handler: Lib = self.anti_spam_handler.lib_handler

        if valid_timestamp_interval is not None:
            if isinstance(valid_timestamp_interval, (str, float)):
                try:
                    valid_timestamp_interval = int(valid_timestamp_interval)
                except (TypeError, ValueError):
                    raise ValueError(
                        "Expected valid_timestamp_interval of type int"
                    ) from None
            elif isinstance(valid_timestamp_interval, int):
                pass
            else:
                raise TypeError("Expected valid_timestamp_interval of type int")

        self.valid_global_interval: int = (
            valid_timestamp_interval or anti_spam_handler.options.message_interval
        )
        self.valid_global_interval = int(self.valid_global_interval)

        self.member_tracking: PluginCache = PluginCache(
            handler=anti_spam_handler, caller=self
        )

        log.info("Plugin ready for usage")

    async def propagate(
        self, message, data: typing.Optional[CorePayload] = None
    ) -> dict:
        """
        Overwrite the base extension to call ``update_cache``
        internally so it can be used as an extension
        """
        await self.update_cache(message, data)
        return {"status": "Cache updated"}

    async def update_cache(self, message, data: CorePayload) -> None:
        """
        Takes the data returned from `propagate`
        and updates this Class's internal cache

        Parameters
        ----------
        message
            The message related to `data's` propagation
        data : CorePayload
            The data returned from `propagate`
        """
        if not isinstance(data, CorePayload):
            raise TypeError("Expected data of type: CorePayload")

        if self.lib_handler.is_dm(message):
            return

        if not data.member_should_be_punished_this_message:
            # They shouldn't be punished so don't increase cache
            return

        member_id = message.author.id
        guild_id = await self.anti_spam_handler.lib_handler.get_guild_id(message)
        timestamp = get_aware_time()

        # We now need to increase their cache
        try:
            addon_data = await self.member_tracking.get_member_data(
                member_id=member_id, guild_id=guild_id
            )

        except (MemberNotFound, GuildNotFound):
            # Store the new member
            member = Member(id=member_id, guild_id=guild_id)
            await self.anti_spam_handler.cache.set_member(member)
            addon_data = []

        except MemberAddonNotFound:
            # Member exists, just an addon doesnt
            addon_data = []

        addon_data.append(timestamp)
        await self.member_tracking.set_member_data(
            member_id, guild_id, addon_data=addon_data
        )

        log.debug("Cache updated for Member(id=%s) in Guild(id%s)", member_id, guild_id)

    async def get_member_count(self, message) -> int:
        """
        Returns how many messages that are still 'valid'
        (counted as spam) a certain member has

        Parameters
        ----------
        message
            The message from which to extract member

        Returns
        -------
        int
            How many times this member has sent a
            message that has been marked as
            'punishment worthy' by AntiSpamHandler
            within the valid interval time period

        Raises
        ------
        MemberNotFound
            The User for the ``message`` could not be found

        """
        if self.lib_handler.is_dm(message):
            raise MemberNotFound("Can't find member's from dm's")

        member_id = message.author.id
        guild_id = await self.anti_spam_handler.lib_handler.get_guild_id(message)

        addon_data = await self.member_tracking.get_member_data(
            guild_id=guild_id, member_id=member_id
        )

        await self.remove_outdated_timestamps(
            addon_data, member_id=member_id, guild_id=guild_id
        )

        return len(addon_data)

    async def remove_outdated_timestamps(
        self, data: typing.List, member_id: int, guild_id: int
    ) -> None:
        """
        This logic works around checking the current
        time vs a messages creation time. If the message
        is older by the config amount it can be cleaned up

        *Generally not called by the end member*

        Parameters
        ==========
        data : List
            The data to work with
        member_id : int
            The id of the member to store on
        guild_id : int
            The id of the guild to store on

        """
        log.debug(
            "Attempting to remove outdated timestamp's for Member(id=%s) in Guild(id=%s)",
            member_id,
            guild_id,
        )
        current_time = get_aware_time()

        async def _is_still_valid(timestamp_obj):
            """
            Given a timestamp, figure out if it hasn't
            expired yet
            """
            difference = current_time - timestamp_obj
            offset = datetime.timedelta(
                milliseconds=await self._get_guild_valid_interval(guild_id=guild_id)
            )

            if difference >= offset:
                return False
            return True

        current_timestamps = []

        for timestamp in data:
            if await _is_still_valid(timestamp):
                current_timestamps.append(timestamp)

        log.debug("Removed 'timestamps' for Member(id=%s)", member_id)

        await self.member_tracking.set_member_data(
            member_id, guild_id, addon_data=current_timestamps
        )

    async def remove_punishments(self, message):
        """
        After you punish someone, call this method
        to 'clean up' there punishments.

        Parameters
        ----------
        message
            The message to extract member from

        Raises
        ------
        TypeError
            Invalid arg

        Notes
        -----
        This will actually create a member internally
        if one doesn't already exist for simplicities sake
        """
        if self.lib_handler.is_dm(message):
            return

        member_id = message.author.id
        guild_id = await self.anti_spam_handler.lib_handler.get_guild_id(message)

        await self.member_tracking.set_member_data(member_id, guild_id, addon_data=[])

    async def _set_guild_valid_interval(
        self, guild_id: int, valid_interval: int
    ) -> None:
        """
        Given an interval, set it internally for
        usage on a guild. This is essentially like
        using custom guild options.

        Parameters
        ----------
        guild_id : int
            The guild to set this on
        valid_interval : int
            The time interval to use

        Raises
        ------
        ValueError
            valid_interval must be a positive number

        """
        try:
            guild_data = await self.member_tracking.get_guild_data(guild_id)
            guild_data["valid_interval"] = valid_interval
            await self.member_tracking.set_guild_data(guild_id, guild_data)
        except (GuildNotFound, GuildAddonNotFound):
            await self.member_tracking.set_guild_data(
                guild_id, {"valid_interval": valid_interval}
            )

    async def _get_guild_valid_interval(self, guild_id: int) -> int:
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
        try:
            guild = await self.member_tracking.get_guild_data(guild_id)
        except GuildNotFound:
            return self.valid_global_interval

        if "valid_interval" not in guild:
            return self.valid_global_interval

        return guild["valid_interval"]

    async def is_spamming(self, message) -> bool:
        """
        Given a message, deduce and return if a member
        is classed as 'spamming' or not based on ``punish_min_amount``

        Parameters
        ----------
        message
            The message to extract guild and member from

        Returns
        -------
        bool
            True if the User is spamming else False

        """
        if self.lib_handler.is_dm(message):
            return False

        try:
            user_count = await self.get_member_count(message=message)
            if user_count >= self.punish_min_amount:
                return True
        except (MemberNotFound, MemberAddonNotFound, GuildNotFound):
            return False
        else:
            return False

    async def do_punishment(self, message, *args, **kwargs) -> None:
        """
        This only exists for if the member wishes to subclass
        this class and implement there own logic for punishments
        here.

        Parameters
        ----------
        message
            The message to extract the guild and member from

        Notes
        -----
        This does nothing unless you subclass
        and implement it yourself.

        """
        pass
