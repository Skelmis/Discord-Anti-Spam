import pytest
from discord.ext import commands  # noqa

from discord.ext.antispam import AntiSpamHandler, PluginCache  # noqa

from discord.ext.antispam.core import Core
from discord.ext.antispam.caches import Memory


class MockClass:
    pass


@pytest.fixture
def create_bot():
    """Creates a commands.Bot instance"""
    return commands.Bot(command_prefix="!")


@pytest.fixture
def create_handler(create_bot):
    """Create a simple handler for usage"""
    return AntiSpamHandler(create_bot)


@pytest.fixture
def create_plugin_cache(create_handler):
    """Creates a PluginCache instance"""
    return PluginCache(create_handler, MockClass())


@pytest.fixture
def create_memory_cache(create_handler):
    return Memory(create_handler)


@pytest.fixture
def create_core(create_handler):
    return Core(create_handler)
