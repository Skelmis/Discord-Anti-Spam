import pytest

from antispam.libs.shared import Base
from tests.mocks import MockedMessage


class TestSharedBase:
    @pytest.mark.asyncio
    async def test_get_substitute_args(self, create_base: Base):
        with pytest.raises(NotImplementedError):
            await create_base.get_substitute_args(MockedMessage().to_mock())
