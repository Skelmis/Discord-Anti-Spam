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
from typing import Dict

from antispam import AntiSpamHandler
from antispam.base_plugin import BasePlugin
from antispam.dataclasses import CorePayload

log = logging.getLogger(__name__)


class Stats(BasePlugin):
    """
    A simplistic approach to aggregating statistics
    across the anti spam package.

    Do note however, it assumes plugins do not error out.
    If a plugin errors out, this will be inaccurate.

    This does play with internals a bit,
    however, it is distributed within the
    library I am okay modifying the base package
    to make this work even better.
    """

    injectable_nonce = "Issa me, Mario!"  # For our `propagate` check

    def __init__(self, anti_spam_handler: AntiSpamHandler):
        super().__init__(is_pre_invoke=False)

        self.data = {
            "pre_invoke_calls": {},
            "after_invoke_calls": {},
            "propagate_calls": 0,
            "guilds": {},
            "members": {},
        }
        self.handler = anti_spam_handler

        log.debug("Plugin ready for usage")

    async def propagate(self, message, data: CorePayload) -> dict:
        log.info("Updating statistics on_propagate")
        for invoker in self.handler.pre_invoke_plugins.keys():
            try:
                self.data["pre_invoke_calls"][invoker]["calls"] += 1
            except KeyError:
                self.data["pre_invoke_calls"][invoker] = {}
                self.data["pre_invoke_calls"][invoker]["calls"] = 1

        for invoker in self.handler.after_invoke_plugins.keys():
            try:
                self.data["after_invoke_calls"][invoker]["calls"] += 1
            except KeyError:
                self.data["after_invoke_calls"][invoker] = {}
                self.data["after_invoke_calls"][invoker]["calls"] = 1

        self.data["propagate_calls"] += 1

        guild_id = await self.handler.lib_handler.get_guild_id(message)

        if guild_id not in self.data["guilds"]:
            self.data["guilds"][guild_id] = {
                "calls": 0,
                "total_messages_punished": 0,
            }

        self.data["guilds"][guild_id]["calls"] += 1

        if message.author.id not in self.data["members"]:
            self.data["members"][message.author.id] = {"calls": 0, "times_punished": 0}

        self.data["members"][message.author.id]["calls"] += 1

        if data.member_should_be_punished_this_message:
            self.data["members"][message.author.id]["times_punished"] += 1
            self.data["guilds"][guild_id]["total_messages_punished"] += 1

        return {"status": "Updated stats!"}

    async def save_to_dict(self) -> Dict:
        return self.data

    @classmethod
    async def load_from_dict(cls, anti_spam_handler: AntiSpamHandler, data: Dict):
        ref = cls(anti_spam_handler)
        ref.data = data
        return ref
