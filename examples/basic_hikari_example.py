import hikari

from antispam import AntiSpamHandler

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
        "antispam": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
        "__main__": {  # if __name__ == '__main__'
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


bot = hikari.GatewayBot(
    token="NzgwNzk3MDU4Nzc2MTcwNTQ2.X70T7Q.aYJJ3ECIEexjhuuRhdG66L1sM1k",
    logs=LOGGING_CONFIG,
)
handler = AntiSpamHandler(bot, is_using_hikari=True)


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    await handler.propagate(event.message)


bot.run()
