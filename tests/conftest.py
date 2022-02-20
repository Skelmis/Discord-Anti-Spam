from typing import Any, Dict, List
from unittest.mock import Mock

import pytest
from attr import asdict
from discord.ext import commands  # noqa

from antispam import AntiSpamHandler, PluginCache
from antispam.caches import MemoryCache
from antispam.caches.mongo import MongoCache
from antispam.core import Core
from antispam.dataclasses import Guild, Member, Message
from antispam.libs.dpy import DPY
from antispam.libs.shared import Base, TimedCache
from antispam.plugins import AdminLogs, AntiMassMention, AntiSpamTracker, Stats
from examples.custom_multistage_punishments.AntiSpamTrackerSubclass import (
    MyCustomTracker,
)
from tests.mocks import MockedMember
from tests.mocks.mock_document import MockedDocument


class MockClass:
    pass


class MockedMongoCache(MongoCache):
    def __init__(self, handler, member_data, guild_data):
        self.handler = handler
        self.guilds: MockedDocument = MockedDocument(guild_data, converter=Guild)
        self.members: MockedDocument = MockedDocument(member_data, converter=Member)


@pytest.fixture
def create_bot():
    """Creates a commands.Bot instance"""
    return commands.Bot(command_prefix="!")


@pytest.fixture
def create_handler():
    """Create a simple handler for usage"""
    mock = MockedMember(mock_type="bot").to_mock()
    mock.get_guild = Mock()
    return AntiSpamHandler(mock)


@pytest.fixture
def create_plugin_cache(create_handler):
    """Creates a PluginCache instance"""
    return PluginCache(create_handler, MockClass())


@pytest.fixture
def create_memory_cache(create_handler):
    return MemoryCache(create_handler)


@pytest.fixture
def create_core(create_handler):
    return Core(create_handler)


@pytest.fixture
def create_anti_mass_mention(create_bot, create_handler):
    return AntiMassMention(create_bot, create_handler)


@pytest.fixture
def create_anti_spam_tracker(create_handler):
    return AntiSpamTracker(create_handler, 3)


@pytest.fixture
def create_stats(create_handler):
    return Stats(create_handler)


@pytest.fixture
def create_dpy_lib_handler(create_handler):
    return DPY(create_handler)


@pytest.fixture
def create_admin_logs(create_handler):
    return AdminLogs(create_handler, "test")


@pytest.fixture
def create_base():
    return Base()


@pytest.fixture
def create_timed_cache() -> TimedCache:
    return TimedCache()


@pytest.fixture()
def create_mongo_cache(create_handler) -> MockedMongoCache:
    guild_data: List[Dict[str, Any]] = [asdict(Guild(1))]
    member_data: List[Dict[str, Any]] = [
        asdict(
            Member(
                1,
                1,
                warn_count=2,
                kick_count=1,
                messages=[
                    Message(1, 1, 1, 1, content="Foo"),
                    Message(2, 1, 1, 1, content="Bar"),
                    Message(3, 1, 1, 1, content="Baz"),
                ],
            ),
            recurse=True,
        ),
        asdict(Member(2, 1)),
    ]

    return MockedMongoCache(create_handler, member_data, guild_data)


@pytest.fixture()
def create_example_tracker_subclass(create_handler) -> MyCustomTracker:
    return MyCustomTracker(create_handler, 3, 1000)
