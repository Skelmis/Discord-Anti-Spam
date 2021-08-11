from typing import Optional

import discord

from .dataclasses import CorePayload

class BaseExtension:
    def __init__(self, is_pre_invoke=True) -> None:
        self.is_pre_invoke = is_pre_invoke

    async def propagate(
        self, message: discord.Message, data: Optional[CorePayload] = None
    ) -> dict:
        """
        This method is called whenever the base ``antispam.propagate`` is called,
        adhering to ``self.is_pre_invoke``

        Parameters
        ----------
        message
        data

        Returns
        -------
        dict
            A dictionary of useful data to the end user

        """
        pass
