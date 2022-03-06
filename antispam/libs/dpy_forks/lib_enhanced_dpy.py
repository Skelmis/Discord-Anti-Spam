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

import discord  # enhanced dpy

from antispam import MissingGuildPermissions
from antispam.libs.dpy import DPY

log = logging.getLogger(__name__)


class EnhancedDPY(DPY):
    def __init__(self, handler):
        self.handler = handler
        self.bot = self.handler.bot

        log.debug(
            "Support for Enhanced DPY is based on docs and is not tested. "
            "If you encounter issues please let me know via the repo."
        )

    async def timeout_member(
        self, member: discord.Member, original_message, until: datetime.timedelta
    ) -> None:
        guild = original_message.guild
        perms = guild.me.guild_permissions
        if not perms.moderate_members:
            raise MissingGuildPermissions(
                "moderate_members is required to timeout members.\n"
                f"Tried timing out Member(id={member.id}) in Guild(id={member.guild.id})"
            )

        await member.edit(
            timeout_until=until, reason="Automated timeout from Discord-Anti-Spam"  # type: ignore
        )

    async def is_member_currently_timed_out(self, member) -> bool:
        return member.timed_out  # type: ignore
