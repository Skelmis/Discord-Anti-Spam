from pincer import Client, Intents
from pincer.objects import UserMessage

from antispam import AntiSpamHandler
from antispam.enums import Library
from examples.jsonLoader import read_json


class Bot(Client):

    def __init__(self):
        super(Bot, self).__init__(
            token=read_json("token").get("token"),
            intents=Intents.all()
        )

        self.antispam = AntiSpamHandler(self, library=Library.PINCER)

    @Client.event
    async def on_ready(self):
        print("Logged in as", self.bot)

    @Client.event
    async def on_message(self, message: UserMessage):
        await self.antispam.propagate(message)  # noqa


if __name__ == '__main__':
    Bot().run()
