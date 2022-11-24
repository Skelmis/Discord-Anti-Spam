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
import logging
import os
from pathlib import Path
from typing import Any, Union, Callable, Optional

from antispam import AntiSpamHandler, CorePayload, LogicError
from antispam.base_plugin import BasePlugin
from antispam.dataclasses import Guild, Member

log = logging.getLogger(__name__)


class AdminLogs(BasePlugin):
    """A plugin design to save admins hassle with
    regard to evidence collection on automated punishments.
    """

    def __init__(
        self,
        handler: AntiSpamHandler,
        log_location: str,
        *,
        punishment_type: Optional[Union[str, Callable]] = None,
        save_all_transcripts: bool = True,
    ):
        """
        Parameters
        ----------
        handler : AntiSpamHandler
            Our AntiSpamHandler instance
        log_location: str
            The directory to store logs in, relative from
            the caller location. This directory should be
            empty or only contain previous output from this plugin.
        punishment_type: Optional[Union[str, Callable]]
            This will be used if sending logs for custom punishments.

            You can also provide a :py:class:`Callable` which should
            return a string to be used as the punishment type. This
            function will be called with 2 arguments.
            Argument 1 is the message, argument 2 is :py:class:`CorePayload`
        save_all_transcripts: bool
            Whether or not to save all transcripts regardless of if
            log channel is set for the guild in question.

            Defaults to True

        Notes
        -----
        This will save transcripts for *every* punishment,
        but it only sends ones to discord if the Guild
        has a log_channel_id set.
        """
        super().__init__(is_pre_invoke=False)

        if handler.options.no_punish:
            log.warning(
                "Using this package while in no_punish mode is likely going to cause issues."
            )

        self.handler = handler
        self.path = log_location
        self._punishment_type: Optional[Union[str, Callable]] = punishment_type
        self.save_all_transcripts: bool = save_all_transcripts

        log.info("Plugin ready for usage")

    async def propagate(
        self, message, data: CorePayload = None
    ) -> Any:  # pragma: no cover
        # This is ignored in coverage as it depends
        # a lot on external calls I'd rather not mock
        # and its tested manually instead
        if not data.member_should_be_punished_this_message:
            # Do nothing unless punished
            return

        author_id = message.author.id
        guild_id = await self.handler.lib_handler.get_guild_id(message)

        log.info(
            "Saving evidence against Member(id=%s) in Guild(id=%s)", author_id, guild_id
        )

        # Extract punishment type
        punishment_type = None
        if data.member_was_warned:
            punishment_type = "warn"

        elif data.member_was_kicked:
            punishment_type = "kick"

        elif data.member_was_banned:
            punishment_type = "ban"

        elif data.member_was_timed_out:
            punishment_type = "timeout"

        else:
            # Lets take a look and try figure out a punishment type
            if self._punishment_type and callable(self._punishment_type):
                punishment_type = str(self._punishment_type(message, data))

            else:
                punishment_type = self._punishment_type or "Unknown Punishment"

        guild: Guild = await self.handler.cache.get_guild(guild_id)
        if not self.save_all_transcripts and not guild.log_channel_id:
            log.debug(
                "Failing to save transcript as %s does not have a log channel set",
                guild.id,
            )
            return

        # Make sure a folder exists for this punishment on this Member within this Guild
        dir_path = os.path.join(
            self.path, str(guild_id), str(author_id), punishment_type
        )
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        # Get existing file count within dir
        current_count = len(os.listdir(dir_path)) + 1

        member: Member = await self.handler.cache.get_member(author_id, guild_id)
        channel_id: int = await self.handler.lib_handler.get_channel_id(message)

        # Open the punishment file
        file_path = os.path.join(dir_path, f"{current_count}.txt")
        with open(file_path, "w") as f:
            # Write headers / rough details
            f.write(f"Author id: {message.author.id}\n-----\n")
            f.write(f"Guild id: {guild_id}\n-----\n")
            f.write(f"Channel of offence: {channel_id}\n-----\n")
            f.write(
                f"Current warn count: {member.warn_count}\n"
                f"Current kick count: {member.kick_count}\n-----\n"
            )
            f.write(
                f"Date & time of the message which triggered this punishment:\n"
                f"{message.created_at.strftime('%I:%M:%S %p, %d/%m/%Y')}\n-----\n"
            )
            f.write(f"Punishment type: {punishment_type.title()}\n-----\n")

            f.write(
                "Each entry following this line represents a message marked as spam.\n\n"
            )

            # Write each message to the file
            for message in member.messages:
                if not message.is_duplicate:
                    # Only write out duplicate messages
                    continue

                f.write(
                    f"{message.creation_time.strftime('%I:%M:%S %p, %d/%m/%Y')} | {message.content}\n-----\n"
                )

        log.debug(
            "Saved evidence against Member(id=%s) in Guild(id=%s) to file at location: %s",
            member.id,
            guild_id,
            file_path,
        )

        if not guild.log_channel_id:
            # No log channel, no problemo
            return

        channel = await self.handler.lib_handler.get_channel_by_id(guild.log_channel_id)

        file = self.handler.lib_handler.get_file(file_path)

        await self.handler.lib_handler.send_guild_log(
            guild,
            f"Punishment logs for a __{punishment_type.title()}__ on <@{author_id}>(`{author_id}`)",
            None,
            channel,
            file=file,
        )
        log.debug(
            "Sent evidence against Member(id=%s) in Guild(id=%s) to the Guild's log channel"
        )
