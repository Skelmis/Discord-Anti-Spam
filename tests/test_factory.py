import datetime

import pytest
from attr import asdict

from antispam import Options
from antispam.dataclasses import Guild, Member, Message
from antispam.factory import FactoryBuilder
from antispam.util import get_aware_time


class TestFactory:
    def test_create_message(self):
        test_dict = {
            "id": 1,
            "content": "Hello World!",
            "guild_id": 2,
            "author_id": 3,
            "channel_id": 4,
            "is_duplicate": True,
            "creation_time": "225596:21:8:3:12:5:2021",
        }
        time = datetime.datetime.strptime(
            "225596:21:8:3:12:5:2021", "%f:%S:%M:%H:%d:%m:%Y"
        )
        message = Message(
            id=1,
            content="Hello World!",
            guild_id=2,
            author_id=3,
            channel_id=4,
            is_duplicate=True,
            creation_time=time,
        )

        test_message = FactoryBuilder.create_message_from_dict(test_dict)

        assert test_message == message

    def test_create_member(self):
        test_data = {
            "id": 1,
            "guild_id": 2,
            "is_in_guild": True,
            "warn_count": 5,
            "kick_count": 6,
            "duplicate_count": 7,
            "duplicate_channel_counter_dict": {},
            "messages": [],
        }
        test_member = FactoryBuilder.create_member_from_dict(test_data)
        member = Member(
            id=1,
            guild_id=2,
            internal_is_in_guild=True,
            warn_count=5,
            kick_count=6,
            duplicate_counter=7,
            duplicate_channel_counter_dict={},
            messages=[],
        )
        assert test_member == member

        test_data_two = {
            "id": 1,
            "guild_id": 2,
            "is_in_guild": True,
            "warn_count": 5,
            "kick_count": 6,
            "duplicate_count": 7,
            "duplicate_channel_counter_dict": {},
            "messages": [
                {
                    "id": 1,
                    "content": "Hello World!",
                    "guild_id": 2,
                    "author_id": 3,
                    "channel_id": 4,
                    "is_duplicate": True,
                    "creation_time": "225596:21:8:3:12:5:2021",
                }
            ],
        }
        test_member_two = FactoryBuilder.create_member_from_dict(test_data_two)

        time = datetime.datetime.strptime(
            "225596:21:8:3:12:5:2021", "%f:%S:%M:%H:%d:%m:%Y"
        )
        message = Message(
            id=1,
            content="Hello World!",
            guild_id=2,
            author_id=3,
            channel_id=4,
            is_duplicate=True,
            creation_time=time,
        )
        member_two = Member(
            id=1,
            guild_id=2,
            internal_is_in_guild=True,
            warn_count=5,
            kick_count=6,
            duplicate_counter=7,
            duplicate_channel_counter_dict={},
            messages=[message],
        )

        assert member_two == test_member_two

    def test_create_guild(self):
        test_data = {"id": 1, "options": asdict(Options()), "members": []}
        test_guild = FactoryBuilder.create_guild_from_dict(test_data)
        guild = Guild(id=1, options=Options())
        assert test_guild == guild

        test_data_two = {
            "id": 1,
            "options": asdict(Options()),
            "members": [
                {
                    "id": 1,
                    "guild_id": 2,
                    "is_in_guild": True,
                    "warn_count": 5,
                    "kick_count": 6,
                    "duplicate_count": 7,
                    "duplicate_channel_counter_dict": {},
                    "messages": [
                        {
                            "id": 1,
                            "content": "Hello World!",
                            "guild_id": 2,
                            "author_id": 3,
                            "channel_id": 4,
                            "is_duplicate": True,
                            "creation_time": "225596:21:8:3:12:5:2021",
                        }
                    ],
                }
            ],
        }
        test_guild_two = FactoryBuilder.create_guild_from_dict(test_data_two)

        time = datetime.datetime.strptime(
            "225596:21:8:3:12:5:2021", "%f:%S:%M:%H:%d:%m:%Y"
        )
        message = Message(
            id=1,
            content="Hello World!",
            guild_id=2,
            author_id=3,
            channel_id=4,
            is_duplicate=True,
            creation_time=time,
        )
        member_two = Member(
            id=1,
            guild_id=2,
            internal_is_in_guild=True,
            warn_count=5,
            kick_count=6,
            duplicate_counter=7,
            duplicate_channel_counter_dict={},
            messages=[message],
        )
        guild_two = Guild(id=1, options=Options())
        guild_two.members[1] = member_two
        assert test_guild_two == guild_two

    def test_clean_old_messages(self):
        member = Member(
            1,
            2,
            messages=[
                Message(1, 2, 3, 4, "Hello"),
                Message(
                    2,
                    2,
                    3,
                    4,
                    "World",
                    creation_time=get_aware_time() - datetime.timedelta(seconds=45),
                ),
            ],
        )
        assert len(member.messages) == 2

        FactoryBuilder.clean_old_messages(member, get_aware_time(), Options())

        assert len(member.messages) == 1
