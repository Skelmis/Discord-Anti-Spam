import datetime
import logging
from copy import deepcopy
from typing import Union, Optional

import discord

from fuzzywuzzy import fuzz

from .exceptions import (
    MissingGuildPermissions,
    MemberNotFound,
    LogicError,
    DuplicateObject,
)
from .dataclasses import Member, Message, CorePayload, Guild
from .util import embed_to_string, transform_message

log = logging.getLogger(__name__)


# noinspection PyProtectedMember
class Core:
    """An abstract way to handle spam tracking on different levels"""

    __slots__ = ("handler", "cache", "options")

    def __init__(self, handler):
        self.handler = handler
        self.options = handler.options
        self.cache = handler.cache  # Shorthand

    async def propagate(self, message: discord.Message, guild: Guild) -> CorePayload:
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

    async def propagate_user(
        self, original_message: discord.Message, guild: Guild
    ) -> CorePayload:
        """
        The internal representation of core functionality.

        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """
        try:
            if original_message.author.id in guild.members:
                member = guild.members[original_message.author.id]
            else:
                member: Member = await self.cache.get_member_data(
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
            current_time=datetime.datetime.now(datetime.timezone.utc),
            channel_id=original_message.channel.id,
        )
        message: Message = self._create_message(original_message)
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
            return CorePayload(
                member_status="Member should be punished, however, was not due to no_punish being True"
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
            guild_message = transform_message(
                self.options.guild_warn_message,
                original_message,
                {"warn_count": member.warn_count, "kick_count": member.kick_count},
            )
            try:
                if isinstance(guild_message, discord.Embed):
                    await channel.send(
                        embed=guild_message,
                        delete_after=self.options.guild_warn_message_delete_after,
                    )
                else:
                    await channel.send(
                        guild_message,
                        delete_after=self.options.guild_warn_message_delete_after,
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

            guild_message = transform_message(
                self.options.guild_kick_message,
                original_message,
                {"warn_count": member.warn_count, "kick_count": member.kick_count},
            )
            user_message = transform_message(
                self.options.member_kick_message,
                original_message,
                {"warn_count": member.warn_count, "kick_count": member.kick_count},
            )
            await self._punish_member(
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

            guild_message = transform_message(
                self.options.guild_ban_message,
                original_message,
                {"warn_count": member.warn_count, "kick_count": member.kick_count},
            )
            user_message = transform_message(
                self.options.member_ban_message,
                original_message,
                {"warn_count": member.warn_count, "kick_count": member.kick_count},
            )
            await self._punish_member(
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
        self, message: discord.Message, core_payload: CorePayload
    ) -> CorePayload:
        """
        The internal representation of core functionality.

        Please see and use :meth:`discord.ext.antispam.AntiSpamHandler`
        """
        # TODO Impl
        return core_payload

    async def _punish_member(
        self,
        original_message: discord.Message,
        member: Member,
        internal_guild: Guild,
        user_message: Union[str, discord.Embed],
        guild_message: Union[str, discord.Embed],
        is_kick: bool,
        user_delete_after: int = None,
        channel_delete_after: int = None,
    ):
        """
        A generic method to handle multiple methods of punishment for a user.
        Currently supports: kicking, banning
        Parameters
        ----------
        original_message : discord.Message
            Where we get everything from :)
        user_message : Union[str, discord.Embed]
            A message to send to the user who is being punished
        guild_message : Union[str, discord.Embed]
            A message to send in the guild for whoever is being punished
        is_kick : bool
            Is it a kick? Else ban
        user_delete_after : int, optional
            An int value denoting the time to
            delete user sent messages after
        channel_delete_after : int, optional
            An int value denoting the time to
            delete channel sent messages after
        Raises
        ======
        MissingGuildPerms
            I lack perms to carry out this punishment
        """
        guild = original_message.guild
        author = original_message.author

        dc_channel = internal_guild.log_channel or original_message.channel

        # Check we have perms to punish
        perms = guild.me.guild_permissions
        if not perms.kick_members and is_kick:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need kick perms to punish someone in {guild.name}"
            )

        elif not perms.ban_members and not is_kick:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need ban perms to punish someone in {guild.name}"
            )

        # We also check they don't own the guild, since ya know...
        elif guild.owner_id == member.id:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I cannot punish {author.display_name}({author.id}) "
                f"because they own this guild. ({guild.name})"
            )

        # Ensure we can actually punish the user, for this
        # we just check our top role is higher then them
        elif guild.me.top_role.position < author.top_role.position:
            log.warning(
                f"I might not be able to punish {author.display_name}({member.id}) in {guild.name}({guild.id}) "
                "because they are higher then me, which means I could lack the ability to kick/ban them."
            )

        sent_message: Optional[discord.Message] = None
        try:
            if isinstance(user_message, discord.Embed):
                sent_message = await author.send(
                    embed=user_message, delete_after=user_delete_after
                )
            else:
                sent_message = await author.send(
                    user_message, delete_after=user_delete_after
                )

        except discord.HTTPException:
            # TODO Make this use options log channel
            await dc_channel.send(
                f"Sending a message to {author.mention} about their {'kick' if is_kick else 'ban'} failed.",
                delete_after=channel_delete_after,
            )
            log.warning(
                f"Failed to message User: ({author.id}) about {'kick' if is_kick else 'ban'}"
            )

        # Even if we can't tell them they are being punished
        # We still need to punish them, so try that
        try:
            if is_kick:
                await guild.kick(
                    member, reason="Automated punishment from DPY Anti-Spam."
                )
                log.info(f"Kicked User: ({member.id})")
            else:
                await guild.ban(
                    member, reason="Automated punishment from DPY Anti-Spam."
                )
                log.info(f"Banned User: ({member.id})")

        except discord.Forbidden as e:
            # In theory we send the failed punishment method
            # here, although we check first so I think its fine
            # to remove it from this part
            raise e from None

        except discord.HTTPException:
            member._in_guild = True
            member.kick_count -= 1
            await dc_channel.send(
                f"An error occurred trying to {'kick' if is_kick else 'ban'}: <@{member.id}>",
                delete_after=channel_delete_after,
            )
            log.warning(
                f"An error occurred trying to {'kick' if is_kick else 'ban'}: {member.id}"
            )
            if sent_message is not None:
                if is_kick:
                    user_failed_message = transform_message(
                        self.options.member_failed_kick_message,
                        original_message,
                        {
                            "warn_count": member.warn_count,
                            "kick_count": member.kick_count,
                        },
                    )
                else:
                    user_failed_message = transform_message(
                        self.options.member_failed_ban_message,
                        original_message,
                        {
                            "warn_count": member.warn_count,
                            "kick_count": member.kick_count,
                        },
                    )
                if isinstance(user_failed_message, discord.Embed):
                    await author.send(
                        embed=user_failed_message,
                        delete_after=user_delete_after,
                    )
                else:
                    await author.send(
                        user_failed_message,
                        delete_after=user_delete_after,
                    )
                await sent_message.delete()

        else:
            try:
                if isinstance(guild_message, discord.Embed):
                    await dc_channel.send(
                        embed=guild_message,
                        delete_after=channel_delete_after,
                    )
                else:
                    await dc_channel.send(
                        guild_message,
                        delete_after=channel_delete_after,
                    )
            except discord.HTTPException:
                log.error(
                    f"Failed to send message.\n"
                    f"Guild: {dc_channel.guild.name}({dc_channel.guild.id})\n"
                    f"Channel: {dc_channel.name}({dc_channel.id})"
                )

        member._in_guild = True

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
