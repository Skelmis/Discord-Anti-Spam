import pytest
from discord.ext import commands  # noqa

from antispam import AntiSpamHandler, PluginCache
from antispam.core import Core
from antispam.caches import MemoryCache
from antispam.libs.dpy import DPY
from antispam.plugins import AntiMassMention, AntiSpamTracker, Stats, AdminLogs
from tests.mocks import MockedMember


class MockClass:
    pass


@pytest.fixture
def create_bot():
    """Creates a commands.Bot instance"""
    return commands.Bot(command_prefix="!")


@pytest.fixture
def create_handler():
    """Create a simple handler for usage"""
    return AntiSpamHandler(MockedMember(mock_type="bot").to_mock())


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
