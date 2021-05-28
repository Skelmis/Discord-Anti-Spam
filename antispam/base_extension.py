import discord
import typing


class BaseExtension:
    def __init__(self) -> None:
        self.is_pre_invoke = True

    async def propagate(
        self, message: discord.Message, data: typing.Optional[dict] = None
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

        """
        pass
