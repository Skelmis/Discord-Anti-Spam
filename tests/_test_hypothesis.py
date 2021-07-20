import pytest

from discord.ext import commands

# noinspection PyUnresolvedReferences
from discord.ext.antispam import (
    PluginCache,
    GuildNotFound,
    MemberNotFound,
    MemberAddonNotFound,
    GuildAddonNotFound,
    Options,
    AntiSpamHandler,
)

from discord.ext.antispam.dataclasses import Member, Guild  # noqa

from hypothesis import given
from hypothesis.strategies import text, dictionaries, floats, lists, datetimes

from .fixtures import create_bot, create_handler, create_plugin_cache, MockClass

"""A test file devoted to hypothesis.
These tests do not run on ci due to time
constraints however they are used for
better test argument coverage
"""


class TestHypoth:
    @pytest.mark.asyncio
    @given(arg=text())
    async def test_set_member_data_text(self, arg):
        """Test the cache sets member addon's correct using text"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, arg)

        assert await plugin_cache.get_member_data(1, 1) == arg

    @pytest.mark.asyncio
    @given(arg=dictionaries(text(), floats()))
    async def test_set_member_data_dictionaries(self, arg):
        """Test the cache sets member addon's correct using dictionaries"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, arg)

        assert await plugin_cache.get_member_data(1, 1) == arg

    @pytest.mark.asyncio
    @given(arg=lists(datetimes()))
    async def test_set_member_data_dictionaries(self, arg):
        """Test the cache sets member addon's correct using lists of datetimes"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, arg)

        assert await plugin_cache.get_member_data(1, 1) == arg

    @pytest.mark.asyncio
    @given(arg=text())
    async def test_set_guild_data_text(self, arg):
        """Test the cache sets guild addon's correct using text"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_guild_data(1)

        await plugin_cache.set_guild_data(1, arg)

        assert await plugin_cache.get_guild_data(1) == arg

    @pytest.mark.asyncio
    @given(arg=dictionaries(text(), floats()))
    async def test_set_guild_data_dictionaries(self, arg):
        """Test the cache sets guild addon's correct using dictionaries"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_guild_data(1)

        await plugin_cache.set_guild_data(1, arg)

        assert await plugin_cache.get_guild_data(1) == arg

    @pytest.mark.asyncio
    @given(arg=lists(datetimes()))
    async def test_set_guild_data_dictionaries(self, arg):
        """Test the cache sets guild addon's correct using lists of datetimes"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_guild_data(1)

        await plugin_cache.set_guild_data(1, arg)

        assert await plugin_cache.get_guild_data(1) == arg
