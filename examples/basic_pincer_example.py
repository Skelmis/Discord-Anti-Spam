import logging

from pincer import Client, Intents
from pincer.objects import UserMessage

from antispam import AntiSpamHandler
from antispam.enums import Library
from examples.jsonLoader import read_json

logging.basicConfig(
    format="%(levelname)-7s | %(asctime)s | %(filename)12s:%(funcName)-12s | %(message)s",
    datefmt="%I:%M:%S %p %d/%m/%Y",
    level=logging.INFO,
)
file = read_json("token")


class Bot(Client):
    @Client.event
    async def on_ready(self):
        print(
            f"Started client on {self.bot}\n"
            "Registered commands: " + ", ".join(self.chat_commands)
        )

    @Client.event
    async def on_message(self, message: UserMessage):
        await self.antispam.propagate(message)  # noqa


intents = Intents.all()
# intents >>= 8

b = Bot(file["token"], intents=intents)
b.antispam = AntiSpamHandler(b, library=Library.PINCER)

b.run()
