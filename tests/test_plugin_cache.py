import pytest
from discord.ext import commands

# noinspection PyUnresolvedReferences
from antispam import (
    AntiSpamHandler,
    GuildAddonNotFound,
    GuildNotFound,
    MemberAddonNotFound,
    MemberNotFound,
    Options,
    PluginCache,
)
from antispam.dataclasses import Guild, Member  # noqa


# noinspection DuplicatedCode
from antispam.enums import Library
from tests.conftest import MockClass


class TestPluginCache:
    def test_init_key(self, create_plugin_cache):
        """Test the cache extracts the caller's name for a key"""
        assert create_plugin_cache.key == "MockClass"

    # MEMBER GET
    @pytest.mark.asyncio
    async def test_get_member_data_fails_on_guild(
        self, create_plugin_cache: PluginCache
    ):
        """Test the cache raises GuildNotFound"""
        with pytest.raises(GuildNotFound):
            await create_plugin_cache.get_member_data(1, 1)

    @pytest.mark.asyncio
    async def test_get_member_data_fails_on_member(
        self, create_plugin_cache: PluginCache
    ):
        """Test the cache raises MemberNotFound"""
        await create_plugin_cache.set_guild_data(1, [])

        with pytest.raises(MemberNotFound):
            await create_plugin_cache.get_member_data(1, 1)

    @pytest.mark.asyncio
    async def test_get_member_data_fails_on_member_addon(
        self, create_plugin_cache: PluginCache, create_handler
    ):
        """Test the cache raises MemberNotFound"""
        await create_handler.cache.set_member(Member(1, 1))

        with pytest.raises(MemberAddonNotFound):
            await create_plugin_cache.get_member_data(1, 1)

    # MEMBER SET
    @pytest.mark.asyncio
    async def test_set_member_data_dictionaries(self):
        """Test the cache sets member addon's correct"""
        plugin_cache = PluginCache(
            AntiSpamHandler(commands.Bot("!"), Library.DPY), MockClass()
        )
        arg = {"test": "tester"}

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, arg)

        assert await plugin_cache.get_member_data(1, 1) == arg

    # GUILD GET
    @pytest.mark.asyncio
    async def test_get_guild_data_fails(self, create_plugin_cache: PluginCache):
        """Test the cache raises GuildNotFound"""
        with pytest.raises(GuildNotFound):
            await create_plugin_cache.get_guild_data(1)

    @pytest.mark.asyncio
    async def test_get_guild_data_fails_on_guild_addon(
        self, create_plugin_cache: PluginCache, create_handler
    ):
        """Test the cache raises GuildAddonNotFound"""
        await create_handler.cache.set_guild(Guild(1, Options()))

        with pytest.raises(GuildAddonNotFound):
            await create_plugin_cache.get_guild_data(1)

    # GUILD SET
    @pytest.mark.asyncio
    async def test_set_guild_data_text(self):
        """Test the cache sets guild addon's correct using text"""
        plugin_cache = PluginCache(
            AntiSpamHandler(commands.Bot("!"), Library.DPY), MockClass()
        )

        arg = "Hello world"

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_guild_data(1)

        await plugin_cache.set_guild_data(1, arg)

        assert await plugin_cache.get_guild_data(1) == arg

    @pytest.mark.asyncio
    async def test_set_member_keyerror(self):
        """A test to test set_member_data throws a keyerror"""
        plugin_cache = PluginCache(
            AntiSpamHandler(commands.Bot("!"), Library.DPY), MockClass()
        )
        await plugin_cache.set_guild_data(1, "A test")
        with pytest.raises(MemberNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, "A member test")
