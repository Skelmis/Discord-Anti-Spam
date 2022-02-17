import ast
import logging
from copy import deepcopy
from string import Template
from typing import Dict, Union

from antispam.libs.shared import SubstituteArgs

log = logging.getLogger(__name__)


class Base:
    """A base Library feature class which implements shared functionality."""

    async def get_substitute_args(self, message) -> SubstituteArgs:
        """

        Parameters
        ----------
        message
            Message used to create SubstituteArgs

        Returns
        -------
        SubstituteArgs

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def lib_embed_as_dict(self, embed) -> Dict:
        """
        Parameters
        ----------
        embed
            Your libraries embed object.

        Returns
        -------
        dict
            The embed in dict form

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def dict_to_lib_embed(self, data: Dict):
        """
        Parameters
        ----------
        data: dict
            The embed as a dictionary, used
            to build a an embed object for your library.

        Returns
        -------
        Any
            Your libraries embed object.

        Warnings
        --------
        Lib classes must implement this.
        """
        raise NotImplementedError

    async def substitute_args(
        self,
        content,
        message,
        warn_count: int,
        kick_count: int,
    ) -> str:
        substitute_args: SubstituteArgs = await self.get_substitute_args(message)
        log.debug(
            "Substituting arguments on Message(id=%s) for Member(id=%s)",
            message.id,
            substitute_args.member_id,
        )

        return Template(content).safe_substitute(
            {
                "MEMBERID": substitute_args.member_id,
                "MEMBERNAME": substitute_args.member_name,
                "MEMBERAVATAR": substitute_args.member_avatar,
                "MENTIONMEMBER": substitute_args.mention_member,
                "BOTID": substitute_args.bot_id,
                "BOTNAME": substitute_args.bot_name,
                "BOTAVATAR": substitute_args.bot_avatar,
                "MENTIONBOT": substitute_args.mention_bot,
                "GUILDID": substitute_args.guild_id,
                "GUILDNAME": substitute_args.guild_name,
                "GUILDICON": substitute_args.guild_icon,
                "TIMESTAMPNOW": substitute_args.timestamp_now,
                "TIMESTAMPTODAY": substitute_args.timestamp_today,
                "WARNCOUNT": warn_count,
                "KICKCOUNT": kick_count,
            }
        )

    async def embed_to_string(self, embed) -> str:
        content = ""
        embed = await self.lib_embed_as_dict(embed)
        log.debug("Converting the following to a string, %s", embed)

        if "title" in embed:
            content += f"{embed['title']}\n"

        if "description" in embed:
            content += f"{embed['description']}\n"

        if "footer" in embed:
            if "text" in embed["footer"]:
                content += f"{embed['footer']['text']}\n"

        if "author" in embed:
            content += f"{embed['author']['name']}\n"

        if "fields" in embed:
            for field in embed["fields"]:
                content += f"{field['name']}\n{field['value']}\n"

        return content

    async def dict_to_embed(
        self, data: dict, message, warn_count: int, kick_count: int
    ):
        allowed_avatars = ["$MEMBERAVATAR", "$BOTAVATAR", "$GUILDICON"]
        data: dict = deepcopy(data)
        log.debug("Converting the following to an embed, %s", data)

        if "title" in data:
            data["title"] = await self.substitute_args(
                data["title"], message, warn_count, kick_count
            )

        if "description" in data:
            data["description"] = await self.substitute_args(
                data["description"], message, warn_count, kick_count
            )

        if "footer" in data:
            if "text" in data["footer"]:
                data["footer"]["text"] = await self.substitute_args(
                    data["footer"]["text"], message, warn_count, kick_count
                )

            if "icon_url" in data["footer"]:
                if data["footer"]["icon_url"] in allowed_avatars:
                    data["footer"]["icon_url"] = await self.substitute_args(
                        data["footer"]["icon_url"], message, warn_count, kick_count
                    )

        if "author" in data:
            # name 'should' be required
            data["author"]["name"] = await self.substitute_args(
                data["author"]["name"], message, warn_count, kick_count
            )

            if "icon_url" in data["author"]:
                if data["author"]["icon_url"] in allowed_avatars:
                    data["author"]["icon_url"] = await self.substitute_args(
                        data["author"]["icon_url"], message, warn_count, kick_count
                    )

        if "fields" in data:
            for field in data["fields"]:
                name = await self.substitute_args(
                    field["name"], message, warn_count, kick_count
                )
                value = await self.substitute_args(
                    field["value"], message, warn_count, kick_count
                )
                field["name"] = name
                field["value"] = value

                if "inline" not in field:
                    field["inline"] = True

        if "timestamp" in data:  # pragma: no cover
            data["timestamp"] = message.created_at.isoformat()

        if "colour" in data:
            data["color"] = data["colour"]

        data["type"] = "rich"

        return await self.dict_to_lib_embed(data)

    async def transform_message(
        self,
        content: Union[str, dict],
        message,
        warn_count: int,
        kick_count: int,
    ):
        if isinstance(content, str):
            return await self.substitute_args(content, message, warn_count, kick_count)

        return await self.dict_to_embed(content, message, warn_count, kick_count)

    async def visualizer(
        self,
        content: str,
        message,
        warn_count: int = 1,
        kick_count: int = 2,
    ):
        log.debug("Attempting to visualize %s", content)
        if content.startswith("{"):
            content = ast.literal_eval(content)

        return await self.transform_message(content, message, warn_count, kick_count)
