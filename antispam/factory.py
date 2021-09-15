import logging
from copy import deepcopy
import datetime

from .dataclasses import Guild, Member, Message, Options


log = logging.getLogger(__name__)


class FactoryBuilder:
    """A factory to build dataclasses from dictionaries"""

    @staticmethod
    def create_guild_from_dict(guild_data: dict) -> Guild:
        guild: Guild = Guild(
            id=guild_data["id"], options=Options(**guild_data["options"])
        )

        for member in guild_data["members"]:
            guild.members[member["id"]] = FactoryBuilder.create_member_from_dict(member)

        log.debug("Created Guild (%s) from dict", guild.id)

        return guild

    @staticmethod
    def create_member_from_dict(member_data) -> Member:
        member: Member = Member(id=member_data["id"], guild_id=member_data["guild_id"])
        member._in_guild = member_data["is_in_guild"]
        member.warn_count = member_data["warn_count"]
        member.kick_count = member_data["kick_count"]
        member.duplicate_counter = member_data["duplicate_count"]
        member.duplicate_channel_counter_dict = deepcopy(
            member_data["duplicate_channel_counter_dict"]
        )

        for message_data in member_data["messages"]:
            member.messages.append(
                FactoryBuilder.create_message_from_dict(message_data)
            )

        log.debug("Created Member (%s) from dict", member.id)

        return member

    @staticmethod
    def create_message_from_dict(message_data) -> Message:
        message = Message(
            id=message_data["id"],
            content=message_data["content"],
            guild_id=message_data["guild_id"],
            author_id=message_data["author_id"],
            channel_id=message_data["channel_id"],
        )
        message.is_duplicate = message_data["is_duplicate"]
        message.creation_time = datetime.datetime.strptime(
            message_data["creation_time"], "%f:%S:%M:%H:%d:%m:%Y"
        )
        log.debug("Created Message (%s) from dict", message.id)

        return message
