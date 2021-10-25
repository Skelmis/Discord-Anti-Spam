import hikari

from antispam import AntiSpamHandler
from antispam.enums import Library
from examples.jsonLoader import read_json

file = read_json("token")
bot = hikari.GatewayBot(
    token=file["token"],
)

handler = AntiSpamHandler(bot, library=Library.HIKARI)


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    await handler.propagate(event.message)


bot.run()
