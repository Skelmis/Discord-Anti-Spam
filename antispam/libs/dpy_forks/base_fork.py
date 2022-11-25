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

from antispam.libs.dpy import DPY
from antispam.libs.shared import SubstituteArgs

log = logging.getLogger(__name__)


class BaseFork(DPY):
    async def get_substitute_args(self, message) -> SubstituteArgs:
        member_avatar = str(message.author.display_avatar)
        bot_avatar = str(message.guild.me.display_avatar)

        guild_icon = message.guild.icon
        guild_icon = guild_icon.url if guild_icon else ""

        return SubstituteArgs(
            bot_id=message.guild.me.id,
            bot_name=message.guild.me.name,
            bot_avatar=bot_avatar,
            guild_id=message.guild.id,
            guild_icon=guild_icon,
            guild_name=message.guild.name,
            member_id=message.author.id,
            member_name=message.author.display_name,
            member_avatar=member_avatar,
        )

    def get_author_name_from_message(self, message) -> str:
        return message.author.display_name
