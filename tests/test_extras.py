import pytest

from discord.ext.antispam.base_extension import BaseExtension  # noqa

from discord.ext.antispam.enums.state import ASHEnum
from tests.mocks import MockedMessage

"""Some simple tests which don't need a whole file"""


def test_base_init():
    b = BaseExtension()
    assert type(b) == BaseExtension


@pytest.mark.asyncio
async def test_base_prop():
    b = BaseExtension()
    c = await b.propagate(MockedMessage().to_mock())
    assert c is None


def test_state_enum():
    assert ASHEnum.BAN.value == 0
    assert ASHEnum.KICK.value == 1
    assert ASHEnum.WARN_COUNTER.value == 2
    assert ASHEnum.KICK_COUNTER.value == 3
