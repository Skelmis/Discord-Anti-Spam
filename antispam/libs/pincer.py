import ast
import asyncio
import datetime
import logging
from copy import deepcopy
from functools import lru_cache
from pprint import pprint
from string import Template
from typing import Optional, Union, List, Dict
from unittest.mock import AsyncMock

import pincer
from pincer.core.http import HTTPClient
from pincer.exceptions import PincerError
from pincer.objects.guild import TextChannel

from antispam import (
    InvalidMessage,
    LogicError,
    PropagateFailure,
    MissingGuildPermissions,
)
from antispam.abc import Lib
from antispam.dataclasses import Member, Guild, Message
from antispam.dataclasses.propagate_data import PropagateData

from pincer import objects

log = logging.getLogger(__name__)


# noinspection PyProtocol
class Pincer(Lib):
    def __init__(self, handler):
        self.handler = handler
        self.bot: pincer.Client = self.handler.bot

    async def check_message_can_be_propagated(
        self, message: objects.UserMessage
    ) -> PropagateData:
        if not isinstance(message, (objects.UserMessage, AsyncMock)):
            raise PropagateFailure(
                data={"status": "Expected message of type discord.Message"}
            )

        # Ensure we only moderate actual guild messages
        if not message.guild_id:
            log.debug(
                "Message(id=%s) from Member(id=%s) was not in a guild",
                message.id,
                message.author.id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from dm's"})

        # The bot is immune to spam
        if message.author.id == self.bot.bot.id:
            log.debug("Message(id=%s) was from myself", message.id)
            raise PropagateFailure(
                data={"status": "Ignoring messages from myself (the bot)"}
            )

        # Return if ignored bot
        if self.handler.options.ignore_bots and message.author.bot:
            log.debug(
                "I ignore bots, and this is a bot message with author(id=%s)",
                message.author.id,
            )
            raise PropagateFailure(data={"status": "Ignoring messages from bots"})

        # Return if ignored guild
        if message.guild_id in self.handler.options.ignored_guilds:
            log.debug("Ignored Guild(id=%s)", message.guild_id)
            raise PropagateFailure(
                data={"status": f"Ignoring this guild: {message.guild_id}"}
            )

        # Return if ignored member
        if message.author.id in self.handler.options.ignored_members:
            log.debug(
                "The Member(id=%s) who sent this message is ignored", message.author.id
            )
            raise PropagateFailure(
                data={"status": f"Ignoring this member: {message.author.id}"}
            )

        # Return if ignored channel
        if message.channel_id in self.handler.options.ignored_channels:
            log.debug("channel(id=%s) is ignored", message.channel_id)
            raise PropagateFailure(
                data={"status": f"Ignoring this channel: {message.channel_id}"}
            )

        # Return if member has an ignored role
        try:
            member: objects.GuildMember = await objects.GuildMember.from_id(
                self.bot, message.guild_id, message.author.id
            )
            for item in member.roles:
                if item in self.handler.options.ignored_roles:
                    log.debug(
                        "Ignoring Member(id=%s) as they have an ignored Role(id/name=%S)",
                        message.author.id,
                        item,
                    )
                    raise PropagateFailure(
                        data={"status": f"Ignoring this role: {item}"}
                    )
        except AttributeError:
            log.warning(
                "Could not compute ignored_roles for %s(%s)",
                message.author.username,
                message.author.id,
            )

        perms = await self.get_guild_member_perms(message.guild_id, self.bot.bot.id)
        # Me dummy thiccc?
        kick_members = bool(perms << 1)
        ban_members = bool(perms << 2)
        has_perms = kick_members and ban_members

        return PropagateData(
            guild_id=message.guild_id,
            member_name=message.author.username,
            member_id=message.author.id,
            has_perms_to_make_guild=has_perms,
        )

    async def substitute_args(
        self,
        message: str,
        original_message: objects.UserMessage,
        warn_count: int,
        kick_count: int,
    ) -> str:
        client: pincer.Client = self.bot
        guild: objects.Guild = await objects.Guild.from_id(
            client, original_message.guild_id
        )

        return Template(message).safe_substitute(
            {
                "MENTIONMEMBER": original_message.author.mention,
                "MEMBERNAME": original_message.author.username,
                "MEMBERID": original_message.author.id,
                "BOTNAME": client.bot.username,
                "BOTID": client.bot.id,
                "GUILDID": guild.id,
                "GUILDNAME": guild.name,
                "TIMESTAMPNOW": datetime.datetime.now().strftime(
                    "%I:%M:%S %p, %d/%m/%Y"
                ),
                "TIMESTAMPTODAY": datetime.datetime.now().strftime("%d/%m/%Y"),
                "WARNCOUNT": warn_count,
                "KICKCOUNT": kick_count,
                "MEMBERAVATAR": original_message.author.avatar,
                "BOTAVATAR": client.bot.avatar,
                "GUILDICON": guild.icon,
            }
        )

    async def embed_to_string(self, embed: objects.Embed) -> str:
        content = ""
        embed = embed.to_dict()

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
        self,
        data: dict,
        message: objects.UserMessage,
        warn_count: int,
        kick_count: int,
    ):
        allowed_avatars = ["$MEMBERAVATAR", "$BOTAVATAR", "$GUILDICON"]
        data: dict = deepcopy(data)

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

        if "timestamp" in data:
            datetime_msg = datetime.datetime.fromtimestamp(message.id.timestamp)
            data["timestamps"] = datetime_msg.isoformat()

        if "colour" in data:
            data["color"] = data["colour"]

        return objects.Embed.from_dict(data)

    async def transform_message(
        self,
        item: Union[str, dict],
        message: objects.UserMessage,
        warn_count: int,
        kick_count: int,
    ):
        if isinstance(item, str):
            return await self.substitute_args(item, message, warn_count, kick_count)

        return await self.dict_to_embed(item, message, warn_count, kick_count)

    async def visualizer(
        self,
        content: str,
        message: objects.UserMessage,
        warn_count: int = 1,
        kick_count: int = 2,
    ):
        if content.startswith("{"):
            content: dict = ast.literal_eval(content)

        return await self.transform_message(content, message, warn_count, kick_count)

    async def create_message(self, message: objects.UserMessage) -> Message:
        log.debug(
            "Attempting to create a new message for author(id=%s) in Guild(%s)",
            message.author.id,
            message.guild_id,
        )
        if not bool(message.content and message.content.strip()):
            if not message.embeds and not message.attachments:
                raise LogicError

            if not message.embeds:
                # We don't check agaisn't attachments
                raise InvalidMessage

            embed = message.embeds[0]
            if not isinstance(embed, objects.Embed):
                raise LogicError

            content = await self.embed_to_string(embed)
        else:
            content = message.content

        if self.handler.options.delete_zero_width_chars:
            content = (
                content.replace("u200B", "")
                .replace("u200C", "")
                .replace("u200D", "")
                .replace("u200E", "")
                .replace("u200F", "")
                .replace("uFEFF", "")
            )

        return Message(
            id=message.id,
            channel_id=message.channel_id,
            guild_id=message.guild_id,
            author_id=message.author.id,
            content=content,
        )

    async def send_guild_log(
        self,
        guild,
        message: Union[str, objects.Embed],
        delete_after_time: Optional[int],
        original_channel: Union[objects.Channel, TextChannel],
        file: objects.File = None,
    ) -> None:
        try:
            if not guild.log_channel_id:
                log.debug(
                    "Guild(id=%s) has no log channel set, not sending message.",
                    guild.id,
                )
                return

            channel: int = guild.log_channel_id

            channel: objects.Channel = await self.bot.get_channel(channel)

            if isinstance(message, str):
                pincer_message = objects.Message(content=message, attachments=file)
            else:
                pincer_message = objects.Message(embeds=[message], attachments=file)

            msg = await channel.send(pincer_message)

            await asyncio.sleep(delete_after_time)
            await msg.delete()

            log.debug("Sent message to log channel in Guild(id=%s)", guild.id)
        except PincerError:
            log.error(
                "Failed to send log message in Guild(id=%s). HTTPException", guild.id
            )

    async def punish_member(
        self,
        original_message: objects.UserMessage,
        member: Member,
        internal_guild: Guild,
        user_message,
        guild_message,
        is_kick: bool,
        user_delete_after: int = None,
        channel_delete_after: int = None,
    ):
        guild: objects.Guild = await objects.Guild.from_id(
            self.bot, original_message.guild_id
        )
        author = original_message.author
        guild_me: objects.GuildMember = await objects.GuildMember.from_id(
            self.bot, original_message.guild_id, self.bot.bot.id
        )
        guild_member: objects.GuildMember = await objects.GuildMember.from_id(
            self.bot, original_message.guild_id, original_message.author.id
        )

        async def get_hoisted(member: objects.GuildMember) -> int:
            if not member.roles:
                # TODO return guild's default role
                pass

            roles = list(map(int, member.roles))
            return max(roles)

        my_top_role: objects.Role = await objects.Role.from_id(
            self.bot, original_message.guild_id, await get_hoisted(guild_me)
        )
        author_top_role: objects.Role = await objects.Role.from_id(
            self.bot, original_message.guild_id, await get_hoisted(guild_member)
        )
        my_top_role_pos: int = my_top_role.position
        author_top_role_pos: int = author_top_role.position

        # Check we have perms to punish
        perms: int = await self.get_guild_member_perms(
            original_message.guild_id, self.bot.bot.id
        )
        kick_members = bool(perms << 1)
        ban_members = bool(perms << 2)
        if not kick_members and is_kick:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need kick perms to punish someone in {guild.name}"
            )

        elif not ban_members and not is_kick:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I need ban perms to punish someone in {guild.name}"
            )

        # We also check they don't own the guild, since ya know...
        elif guild.owner_id == member.id:
            member._in_guild = True
            member.kick_count -= 1
            raise MissingGuildPermissions(
                f"I cannot punish {author.username}({author.id}) "
                f"because they own this guild. ({guild.name})"
            )

        elif my_top_role_pos < author_top_role_pos:
            log.warning(
                "I might not be able to punish %s(%s) in Guild: %s(%s) "
                "because they are higher then me, which means I could lack the ability to kick/ban them.",
                author.username,
                member.id,
                guild.name,
                guild.id,
            )

        sent_message: Optional[objects.UserMessage] = None
        try:
            await self.send_message_to_(
                target=author,
                message=user_message,
                delete_after_time=user_delete_after,
                mention=original_message.author.mention,
            )

        except pincer.exceptions.PincerError:
            channel: objects.Channel = await objects.Channel.from_id(
                self.bot, original_message.channel_id
            )
            await self.send_guild_log(
                guild=internal_guild,
                message=f"Sending a message to {author.mention} about their {'kick' if is_kick else 'ban'} failed.",
                delete_after_time=channel_delete_after,
                original_channel=channel,
            )
            log.warning(
                f"Failed to message Member(id=%s) about {'kick' if is_kick else 'ban'}",
                author.id,
            )

        # Even if we can't tell them they are being punished
        # We still need to punish them, so try that
        try:
            if is_kick:
                await guild.kick(
                    member.id, reason="Automated punishment from DPY Anti-Spam."
                )

                log.info("Kicked Member(id=%s)", member.id)
            else:
                await guild.ban(
                    member.id, reason="Automated punishment from DPY Anti-Spam."
                )
                log.info("Banned Member(id=%s)", member.id)

        except pincer.exceptions.ForbiddenError as e:
            # In theory we send the failed punishment method
            # here, although we check first so I think its fine
            # to remove it from this part
            raise e from None

        except pincer.exceptions.PincerError:
            channel: objects.Channel = await self.bot.get_channel(
                original_message.channel_id
            )
            member._in_guild = True
            member.kick_count -= 1
            await self.send_guild_log(
                guild=internal_guild,
                message=f"An error occurred trying to {'kick' if is_kick else 'ban'}: <@{member.id}>",
                delete_after_time=channel_delete_after,
                original_channel=channel,
            )
            log.warning(
                "An error occurred trying to %s: Member(id=%s)",
                {"kick" if is_kick else "ban"},
                member.id,
            )
            if sent_message is not None:
                if is_kick:
                    user_failed_message = await self.transform_message(
                        self.handler.options.member_failed_kick_message,
                        original_message,
                        member.warn_count,
                        member.kick_count,
                    )
                else:
                    user_failed_message = await self.transform_message(
                        self.handler.options.member_failed_ban_message,
                        original_message,
                        member.warn_count,
                        member.kick_count,
                    )

                await self.send_guild_log(
                    internal_guild,
                    user_failed_message,
                    channel_delete_after,
                    channel,
                )
                await sent_message.delete()

        else:
            channel: objects.Channel = await self.bot.get_channel(
                original_message.channel_id
            )
            await self.send_guild_log(
                guild=internal_guild,
                message=guild_message,
                delete_after_time=channel_delete_after,
                original_channel=channel,
            )

        member._in_guild = True
        await self.handler.cache.set_member(member)

    async def delete_member_messages(self, member: Member) -> None:
        log.debug(
            "Attempting to delete all duplicate messages for Member(id=%s) in Guild(%s)",
            member.id,
            member.guild_id,
        )
        bot: pincer.Client = self.bot
        for message in member.messages:
            if message.is_duplicate:
                try:
                    http: HTTPClient = bot.http
                    results = await http.get(
                        f"/channels/{message.channel_id}/messages/{message.id}"
                    )
                    actual_message: objects.UserMessage = objects.UserMessage.from_dict(
                        results
                    )

                    await self.delete_message(actual_message)
                except pincer.exceptions.PincerError:
                    continue

    async def delete_message(self, message: objects.UserMessage) -> None:
        try:
            await message.delete()
        except pincer.exceptions.PincerError:
            log.warning(
                "Failed to delete message %s in Guild(id=%s). PincerError",
                message.id,
                message.guild_id,
            )

    async def get_guild_id(self, message: objects.UserMessage) -> int:
        return message.guild_id

    async def get_channel_id(self, message: objects.UserMessage) -> int:
        return message.channel_id

    async def get_message_mentions(self, message: objects.UserMessage) -> List[int]:
        mentions = [m.user.id for m in message.mentions]
        mentions.extend([c.id for c in message.mention_channels])
        mentions.extend([r.id for r in message.mention_roles])
        return mentions

    async def get_channel_from_message(self, message):
        return await self.get_channel_by_id(message.channel_id)

    async def get_channel_by_id(self, channel_id: int):
        return await self.bot.get_channel(channel_id)

    def get_file(self, path: str) -> objects.File:
        return objects.File.from_file(path)

    async def send_message_to_(
        self,
        target: Union[objects.User, objects.GuildMember, objects.Channel],
        message: Union[str, objects.Embed],
        mention: str,
        delete_after_time: Optional[int] = None,
    ) -> None:
        if isinstance(target, (objects.User, objects.GuildMember)):
            await self.send_message_to_user(
                target.id, message, mention, delete_after_time
            )
        else:
            if isinstance(message, str):
                pincer_message = objects.Message(content=message)
            else:
                pincer_message = objects.Message(
                    content=mention,
                    embeds=[message],
                )

            await target.send(pincer_message)

    @lru_cache
    async def get_dm_channel(self, member_id: int) -> Dict:
        return await self.bot.http._HTTPClient__send(
            self.bot.http._HTTPClient__session.post,
            "/users/@me/channels",
            data={"recipient_id": member_id},
        )

    async def send_message_to_user(
        self,
        member_id: int,
        content: Union[str, objects.Embed],
        mention,
        delete_after_time: Optional[int] = None,
    ) -> None:
        dm_channel = await self.get_dm_channel(member_id=member_id)
        channel_id = dm_channel["id"]

        if isinstance(content, str):
            message: Dict = await self.bot.http._HTTPClient__send(
                self.bot.http._HTTPClient__session.post,
                f"/channel/{channel_id}/messages",
                data={"content": content},
            )
        else:
            message: Dict = await self.bot.http._HTTPClient__send(
                self.bot.http._HTTPClient__session.post,
                f"/channel/{channel_id}/messages",
                data={"embeds": [content.to_dict()], "content": mention},
            )

        if not delete_after_time:
            return

        await asyncio.sleep(delete_after_time)
        await self.bot.http.delete(f"/channels/{channel_id}/messages/{message['id']}")

    async def get_guild_member_perms(self, guild_id: int, member_id: int) -> int:
        member = await self.bot.http.get(f"/guilds/{guild_id}/members/{member_id}")
        member_roles = member["roles"]
        guild_roles: List[Dict] = await self.bot.http.get(f"/guilds/{guild_id}/roles")
        # Gotta guess perms from role perms
        actual_roles = []
        for role in guild_roles:
            if role["id"] in member_roles:
                actual_roles.append(role)

        initial = 0x0
        for role in actual_roles:
            initial |= int(role["permissions"], 16)

        if initial << 3:
            # Admin implies all perms
            initial = 0b111111111111111111111111111111111111111

        return initial
