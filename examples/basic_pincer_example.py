import logging

from pincer import Client, Intents
from pincer.objects import UserMessage

from antispam import AntiSpamHandler
from antispam.enums import Library
from examples.jsonLoader import read_json

file = read_json("token")
# logging.basicConfig(
#     format="%(levelname)s | %(asctime)s | %(module)s | %(message)s",
#     datefmt="%d/%m/%Y %I:%M:%S %p",
#     level=logging.DEBUG,
# )


class Bot(Client):
    @Client.event
    async def on_ready(self):
        print(
            f"Started client on {self.bot}\n"
            "Registered commands: " + ", ".join(self.chat_commands)
        )

    @Client.event
    async def on_message(self, message: UserMessage):
        print("on_messages")
        await self.antispam.propagate(message)  # noqa


intents = Intents.all()
# intents >>= 8

b = Bot(file["token"], intents=intents)
b.antispam = AntiSpamHandler(b, library=Library.PINCER)

b.run()
