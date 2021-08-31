from antispam.plugins import Stats  # noqa

from .fixtures import create_bot, create_handler


class TestStats:
    def test_init(self, create_handler):
        Stats(create_handler)
