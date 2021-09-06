import datetime
import logging

from fuzzywuzzy import fuzz

from .exceptions import (
    MemberNotFound,
    LogicError,
    DuplicateObject,
)
from .dataclasses import Member, Message, CorePayload, Guild
from .util import get_aware_time

log = logging.getLogger(__name__)


# noinspection PyProtectedMember
class Core:
    """An abstract way to handle spam tracking on different levels"""

    __slots__ = ("handler", "cache", "options")

    def __init__(self, handler):
        self.handler = handler
        self.options = handler.options
        self.cache = handler.cache  # Shorthand

    async def propagate(self, message, guild: Guild) -> CorePayload:
        """
        The internal representation of core functionality.

        TODO Test this links
        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """

        # To get here it must have passed checks so simply run the relevant methods
        guild_r = await self.propagate_user(message, guild)

        if self.options.is_per_channel_per_guild:
            # TODO Impl
            guild_r = await self.propagate_per_channel_per_guild(message, guild_r)

        return guild_r

    async def propagate_user(self, original_message, guild: Guild) -> CorePayload:
        """
        The internal representation of core functionality.

        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """
        try:
            if original_message.author.id in guild.members:
                member = guild.members[original_message.author.id]
            else:
                member: Member = await self.cache.get_member(
                    member_id=original_message.author.id,
                    guild_id=original_message.guild.id,
                )

            if not member._in_guild:
                return CorePayload(
                    member_status="Bypassing message check since the member isn't seen to be in a guild"
                )

        except MemberNotFound:
            # Create a useable member
            member = Member(
                id=original_message.author.id, guild_id=original_message.guild.id
            )
            guild.members[member.id] = member
            await self.cache.set_guild(guild=guild)

        await self.clean_up(
            member=member,
            current_time=get_aware_time(),
            channel_id=original_message.channel.id,
        )
        message: Message = self.handler.lib_handler.create_message(original_message)
        self._calculate_ratios(message, member)

        # Check again since in theory the above could take awhile
        if not member._in_guild:
            return CorePayload(
                member_status="Bypassing message check since the member isn't seen to be in a guild"
            )

        member.messages.append(message)
        log.info(f"Created Message {message.id} on {member.id}")

        if (
            self._get_duplicate_count(member, channel_id=message.channel_id)
            < self.options.message_duplicate_count
        ):
            return CorePayload()

        # We need to punish the member with something
        log.debug(
            f"Message: ({message.id}) on {member.id} requires some form of punishment"
        )
        # We need to punish the member with something
        return_payload = CorePayload(member_should_be_punished_this_message=True)

        # Delete the message if wanted
        if self.options.delete_spam is True and self.options.no_punish is False:
            await self.handler.lib_handler.delete_message(original_message)

        if self.options.no_punish:
            # User will handle punishments themselves
            return CorePayload(
                member_should_be_punished_this_message=True,
                member_status="Member should be punished, however, was not due to no_punish being True",
            )

        if (
            self.options.warn_only
            or self._get_duplicate_count(member, message.channel_id)
            >= self.options.warn_threshold
            and member.warn_count < self.options.kick_threshold
            and member.kick_count < self.options.ban_threshold
        ):
            """
            WARN
            The member has yet to reach the warn threshold,
            after the warn threshold is reached this will
            then become a kick and so on
            """
            log.debug(f"Attempting to warn: {message.author_id}")
            member.warn_count += 1
            channel = original_message.channel
            guild_message = self.handler.lib_handler.transform_message(
                self.options.guild_warn_message,
                original_message,
                member.warn_count,
                member.kick_count,
            )
            try:
                await self.handler.lib_handler.send_message_to_(
                    channel, guild_message, self.options.guild_warn_message_delete_after
                )
            except Exception as e:
                member.warn_count -= 1
                raise e

            return_payload.member_was_warned = True
            return_payload.member_status = "Member was warned"

        elif (
            member.warn_count >= self.options.kick_threshold
            and member.kick_count < self.options.ban_threshold
        ):
            # KICK
            # Set this to False here to stop processing other messages, we can revert on failure
            member._in_guild = False
            member.kick_count += 1
            log.debug(f"Attempting to kick: {message.author_id}")

            guild_message = self.handler.lib_handler.transform_message(
                self.options.guild_kick_message,
                original_message,
                member.warn_count,
                member.kick_count,
            )
            user_message = self.handler.lib_handler.transform_message(
                self.options.member_kick_message,
                original_message,
                member.warn_count,
                member.kick_count,
            )
            await self.handler.lib_handler.punish_member(
                original_message,
                member,
                guild,
                user_message,
                guild_message,
                True,
                self.options.member_kick_message_delete_after,
                self.options.guild_kick_message_delete_after,
            )

            return_payload.member_was_kicked = True
            return_payload.member_status = "Member was kicked"

        elif member.kick_count >= self.options.ban_threshold:
            # BAN
            # Set this to False here to stop processing other messages, we can revert on failure
            member._in_guild = False
            member.kick_count += 1
            log.debug(f"Attempting to ban: {message.author_id}")

            guild_message = self.handler.lib_handler.transform_message(
                self.options.guild_ban_message,
                original_message,
                member.warn_count,
                member.kick_count,
            )
            user_message = self.handler.lib_handler.transform_message(
                self.options.member_ban_message,
                original_message,
                member.warn_count,
                member.kick_count,
            )
            await self.handler.lib_handler.punish_member(
                original_message,
                member,
                guild,
                user_message,
                guild_message,
                False,
                self.options.member_ban_message_delete_after,
                self.options.guild_ban_message_delete_after,
            )

            return_payload.member_was_banned = True
            return_payload.member_status = "Member was banned"

        else:
            # Supports backwards compat?
            # Not sure if this is required tbh
            raise LogicError

        # Store the updated values
        await self.cache.set_member(member)

        # Finish payload and return
        return_payload.member_warn_count = member.warn_count
        return_payload.member_kick_count = member.kick_count
        return_payload.member_duplicate_count = (
            self._get_duplicate_count(member=member, channel_id=message.channel_id) - 1
        )
        return return_payload

    async def propagate_per_channel_per_guild(
        self, message, core_payload: CorePayload
    ) -> CorePayload:
        """
        The internal representation of core functionality.

        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """
        # TODO Impl
        return core_payload

    async def clean_up(self, member: Member, current_time, channel_id: int):
        """
        This logic works around checking the current
        time vs a messages creation time. If the message
        is older by the config amount it can be cleaned up

        Parameters
        ----------
        member : Member
            The member we want to clean up
        current_time : datetime.datetime
            A reference time used to clean up
            past messages against
        channel_id : int
            The channel to clean messages in
            if this is set to per_channel
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

        # TODO This might need to be deepcopied
        member.messages = current_messages

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

        try:
            channel_id = int(channel_id)
            return member.duplicate_channel_counter_dict[channel_id]
        except (KeyError, TypeError):
            return 1

    def _remove_duplicate_count(self, member: Member, channel_id: int, amount: int = 1):
        """Used when cleaning the cache, to only lower the correct counter"""
        is_per_channel = self.options.per_channel_spam
        if not is_per_channel:
            member.duplicate_counter -= amount
            return

        try:
            member.duplicate_channel_counter_dict[channel_id] -= amount
        except KeyError:
            log.warning(
                "Failed to de-increment duplicate count as the channel id doesnt exist"
            )