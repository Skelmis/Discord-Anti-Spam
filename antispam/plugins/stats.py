from antispam import AntiSpamHandler
from antispam.base_plugin import BasePlugin
from antispam.dataclasses import CorePayload


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

    async def propagate(self, message, data: CorePayload) -> dict:
        for invoker in self.handler.pre_invoke_extensions.keys():
            try:
                self.data["pre_invoke_calls"][invoker]["calls"] += 1
            except KeyError:
                self.data["pre_invoke_calls"][invoker] = {}
                self.data["pre_invoke_calls"][invoker]["calls"] = 1

        for invoker in self.handler.after_invoke_extensions.keys():
            try:
                self.data["after_invoke_calls"][invoker]["calls"] += 1
            except KeyError:
                self.data["after_invoke_calls"][invoker] = {}
                self.data["after_invoke_calls"][invoker]["calls"] = 1

        self.data["propagate_calls"] += 1

        guild_id = self.handler.lib_handler.get_guild_id(message)

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
