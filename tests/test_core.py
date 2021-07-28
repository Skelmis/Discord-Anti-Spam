import pytest

from discord.ext.antispam.dataclasses import Guild, Member, CorePayload, Message

from discord.ext.antispam import Options
from .fixtures import create_bot, create_handler, create_memory_cache, create_core
from .mocks import MockedMessage


class TestCore:
    """A class devoted to testing core.py"""

    @pytest.mark.asyncio
    async def test_user_propagate_skip_guild(self, create_core):
        """Tests if the member gets skipped if not 'in guild'"""
        msg = MockedMessage(author_id=1, guild_id=1).to_mock()
        guild = Guild(1, Options)
        guild.members[1] = Member(1, 1, in_guild=False)

        payload = await create_core.propagate(msg, guild)

        assert payload == CorePayload(
            member_status="Bypassing message check since the member isn't seen to be in a guild"
        )

    @pytest.mark.asyncio
    async def test_clean_up(self, create_core):
        member = Member(1, 1)
        messages = [
            Message(1, 1, 1, 1, "First message"),
            Message(2, 1, 1, 1, "Second message"),
            Message(3, 1, 1, 1, "Third message"),
            Message(4, 1, 1, 1, "Fourth message"),
        ]
        member.messages = messages
