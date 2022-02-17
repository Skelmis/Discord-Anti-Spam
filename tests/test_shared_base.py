import datetime

import discord
import pytest

from antispam.libs.shared import Base
from tests.conftest import MockClass
from tests.mocks import MockedMessage


class TestSharedBase:
    @pytest.mark.asyncio
    async def test_not_implementeds(self, create_base: Base):
        with pytest.raises(NotImplementedError):
            await create_base.get_substitute_args(MockedMessage().to_mock())

        with pytest.raises(NotImplementedError):
            await create_base.lib_embed_as_dict(MockClass())

        with pytest.raises(NotImplementedError):
            await create_base.dict_to_lib_embed(dict())
