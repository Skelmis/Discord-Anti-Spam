import hikari
from antispam import AntiSpamHandler

from antispam.abc import Lib


class Hikari(Lib):
    def __init__(self, handler: AntiSpamHandler):
        self.handler = handler
