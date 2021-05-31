import typing

import discord

from antispam.base_extension import BaseExtension


class AntiMassMention(BaseExtension):
    def __init__(self):
        super().__init__(is_pre_invoke=True)

    async def propagate(
        self, message: discord.Message, data: typing.Optional[dict] = None
    ) -> dict:
        pass
