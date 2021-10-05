import os
from pathlib import Path
from typing import Any

from antispam import CorePayload, AntiSpamHandler
from antispam.base_plugin import BasePlugin
from antispam.dataclasses import Member


class AdminLogs(BasePlugin):
    """A plugin design to save admins hassle with
    regard to evidence collection on automated punishments.
    """

    def __init__(self, handler: AntiSpamHandler, log_location: str):
        """
        Parameters
        ----------
        handler : AntiSpamHandler
            Our AntiSpamHandler instance
        log_location
            The directory to store logs in, relative from
            the caller location. This directory should be
            empty or only contain previous output from this plugin.
        """
        super().__init__(is_pre_invoke=False)

        self.handler = handler
        self.cwd = str(Path(__file__).parents[0])
        self.path = os.path.join(self.cwd, log_location)

    async def propagate(self, message, data: CorePayload = None) -> Any:
        if not data.member_should_be_punished_this_message:
            # Do nothing unless punished
            return

        author_id = message.author.id
        guild_id = self.handler.lib_handler.get_guild_id(message)

        # Extract punishment type
        punishment_type = None
        if data.member_was_warned:
            punishment_type = "warn"

        elif data.member_was_kicked:
            punishment_type = "kick"

        elif data.member_was_banned:
            punishment_type = "ban"

        # Make sure a folder exists for this punishment on this Member within this Guild
        dir_path = os.path.join(self.path, guild_id, author_id, punishment_type)
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        # Get existing file count within dir
        current_count = len(os.listdir(dir_path))

        member: Member = await self.handler.cache.get_member(author_id, guild_id)

        # Open the punishment file
        with open(os.path.join(dir_path, f"{current_count}.txt"), "w") as f:
            # Write headers / rough details
            f.write(
                f"Author name: {message.author.id}\nAuthor id: {message.author.id}\n-----\n"
            )
            f.write(
                f"Current warn count: {member.warn_count}\n"
                f"Current kick count: {member.kick_count}\n-----\n"
            )
            f.write(
                f"Date & time of the message which triggered this punishment:\n"
                f"{message.created_at.strftime('%I:%M:%S %p, %d/%m/%Y')}\n-----\n"
            )
            f.write(f"Punishment type: {punishment_type.title()}\n-----\n\n")

            # Write each message to the file
            for message in member.messages:
                f.write(
                    f"{message.creation_time.strftime('%I:%M:%S %p, %d/%m/%Y')} | {message.content}\n-----\n"
                )
