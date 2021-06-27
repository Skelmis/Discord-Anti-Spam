import datetime
import logging
from copy import deepcopy
from typing import List

import discord

from fuzzywuzzy import fuzz

from . import AntiSpamHandler, MemberNotFound, LogicError, DuplicateObject
from .dataclasses import Guild, Member, Message
from .util import embed_to_string

log = logging.getLogger(__name__)


class Core:
    """An abstract way to handle spam tracking on different levels"""

    __slots__ = ("handler", "cache", "options")

    def __init__(self, handler: AntiSpamHandler):
        self.handler = handler
        self.options = handler.options
        self.cache = handler.cache  # Shorthand

    async def propagate(self, message: discord.Message) -> dict:
        """
        The internal representation of core functionality.

        TODO Test this links
        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """
        return_data = {}

        # To get here it must have passed checks so simply run the relevant methods
        user_r = await self.propagate_user(message)
        return_data["per_user_per_channel"] = user_r

        if self.is_per_channel_per_guild:
            guild_r = await self.propagate_per_channel_per_guild(message)
            return_data["per_channel_per_guild"] = guild_r

        return return_data

    async def propagate_user(self, original_message: discord.Message) -> dict:
        """
        The internal representation of core functionality.

        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """
        try:
            member: Member = await self.cache.get_member(
                member_id=original_message.author.id, guild_id=original_message.guild.id
            )
            if not member._in_guild:
                return {
                    "status": "Bypassing message check since the member isn't seen to be in a guild"
                }
        except MemberNotFound:
            return {
                "status": "Bypassing message check since the member isn't seen to be in a guild"
            }

        await self.clean_up(
            member=member,
            current_time=datetime.datetime.now(datetime.timezone.utc),
            channel_id=original_message.channel.id,
        )
        message: Message = self._create_message(original_message)
        self._calculate_ratios(message, member)

        # Check again since in theory the above could take awhile
        if not member._in_guild:
            return {
                "status": "Bypassing message check since the member isn't seen to be in a guild"
            }
        member.messages.append(message)
        log.info(f"Created Message {message.id} on {member.id}")

        if (
            self._get_duplicate_count(member, channel_id=message.channel_id)
            >= self.options.message_duplicate_count
        ):
            return {"should_be_punished_this_message": False}

        log.debug(
            f"Message: ({message.id}) on {member.id} requires some form of punishment"
        )
        # We need to punish the member with something
        return_data = {"should_be_punished_this_message": True}

        # Delete the message if wanted
        if self.options.delete_spam is True and self.options.no_punish is False:
            try:
                await original_message.delete()
                log.debug(f"Deleted message: {original_message.id}")
            except discord.HTTPException:
                # Failed to delete message
                log.warning(
                    f"Failed to delete message {original_message.id} in guild {original_message.guild.id}"
                )

        if self.options.no_punish:
            # User will handle punishments themselves
            return_data[
                "status"
            ] = "Member should be punished, however, was not due to no_punish being True"
            return return_data

        if (
            self.options.warn_only
            or self._get_duplicate_count(member, message.channel_id)
            >= self.options.warn_threshold
            and member.warn_count < self.options.kick_threshold
            and member.kick_count < self.options.ban_threshold
        ):
            """
            The member has yet to reach the warn threshold,
            after the warn threshold is reached this will
            then become a kick and so on
            """
            log.debug(f"Attempting to warn: {message.author_id}")
            # TODO Finish impl

    async def propagate_per_channel_per_guild(self, message: discord.Message) -> dict:
        """
        The internal representation of core functionality.

        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """

    async def clean_up(self, member: Member, current_time, channel_id: int):
        """
        This logic works around checking the current
        time vs a messages creation time. If the message
        is older by the config amount it can be cleaned up
        """
        log.debug("Attempting to remove outdated Message's")

        def _is_still_valid(message_obj):
            """
            Given a message, figure out if it hasn't
            expired yet based on timestamps
            """
            difference = current_time - message_obj.creation_time
            offset = datetime.timedelta(milliseconds=self.options.message_interval)

            if difference >= offset:
                return False
            return True

        current_messages = []
        outstanding_messages = []

        for message in member.messages:
            if _is_still_valid(message):
                current_messages.append(message)
            else:
                outstanding_messages.append(message)

        # TODO Try NOT deepcopying here
        member.messages = deepcopy(current_messages)

        # Now if we have outstanding messages we need
        # to process them and see if we need to decrement
        # the duplicate counter as we are removing them from
        # the queue otherwise everything stacks up
        for outstanding_message in outstanding_messages:
            if outstanding_message.is_duplicate:
                self._remove_duplicate_count(member, channel_id)
                log.debug(f"Removing duplicate Message: {outstanding_message.id}")
            log.debug(f"Removing Message: {outstanding_message.id}")

    def _calculate_ratios(
        self,
        message: Message,
        member: Member,
    ) -> None:
        """
        Calculates a messages relation to other messages
        """
        for message_obj in member.messages:
            # This calculates the relation to each other
            if message == message_obj:
                raise DuplicateObject

            elif (
                self.options.per_channel_spam
                and message.channel_id != message_obj.channel_id
            ):
                # This user's spam should only be counted per channel
                # and these messages are in different channel
                continue

            elif (
                fuzz.token_sort_ratio(message.content, message_obj.content)
                >= self.options.message_duplicate_accuracy
            ):
                """
                The handler works off an internal message duplicate counter
                so just increment that and then let our logic process it later
                """
                self._increment_duplicate_count(member, channel_id=message.channel_id)
                message.is_duplicate = True

                if (
                    self._get_duplicate_count(member, channel_id=message.channel_id)
                    >= self.options.message_duplicate_count
                ):
                    break

    def _create_message(self, message: discord.Message) -> Message:
        """Used to create a valid message object
        Raises
        ------
        LogicError
            Not worth creating a message
        """
        if not bool(message.content and message.content.strip()):
            if not message.embeds:
                raise LogicError

            embed = message.embeds[0]
            if not isinstance(embed, discord.Embed):
                raise LogicError

            if embed.type.lower() != "rich":
                raise LogicError

            content = embed_to_string(embed)
        else:
            content = message.clean_content

        if self.options.delete_zero_width_chars:
            content = (
                content.replace("u200B", "")
                .replace("u200C", "")
                .replace("u200D", "")
                .replace("u200E", "")
                .replace("u200F", "")
                .replace("uFEFF", "")
            )

        return Message(
            id=message.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id,
            author_id=message.author.id,
            content=content,
        )

    def _increment_duplicate_count(
        self, member: Member, channel_id: int, amount: int = 1
    ):
        """A helper method to increment the correct duplicate counter, global or not."""
        is_per_channel = self.options.per_channel_spam
        if not is_per_channel:
            # Just use the regular int, should save overhead
            # for those who dont use per_channel_spam
            member.duplicate_counter += amount

        # We need a custom channel to save stuff in
        elif channel_id not in member.duplicate_channel_counter_dict:
            # since we need an extra 1 by default
            member.duplicate_channel_counter_dict[channel_id] = amount + 1

        else:
            member.duplicate_channel_counter_dict[channel_id] += amount

    def _get_duplicate_count(self, member: Member, channel_id: int = None) -> int:
        """A helper method to get the correct duplicate counter based on settings"""
        is_per_channel = self.options.per_channel_spam
        if not is_per_channel:
            return member.duplicate_counter

        channel_id = int(channel_id)

        if channel_id not in member.duplicate_channel_counter_dict:
            return 1

        else:
            return member.duplicate_channel_counter_dict[channel_id]

    def _remove_duplicate_count(self, member: Member, channel_id: int, amount: int = 1):
        """Used when cleaning the cache, to only lower the correct counter"""
        is_per_channel = self.options.per_channel_spam
        if not is_per_channel:
            member.duplicate_counter -= amount

        elif channel_id not in member.duplicate_channel_counter_dict:
            log.warning(
                "Failed to de-increment duplicate count as the channel id doesnt exist"
            )

        else:
            member.duplicate_channel_counter_dict[channel_id] -= amount
