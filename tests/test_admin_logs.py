import pytest

from antispam import CorePayload, GuildNotFound, LogicError
from antispam.plugins import AdminLogs

from .mocks import MockedMessage


class TestAdminLogs:
    def test_init(self, create_handler):
        cls = AdminLogs(create_handler, "test")
        assert cls.path == "test"

        create_handler.options.no_punish = True
        AdminLogs(create_handler, "x")

    @pytest.mark.asyncio
    async def test_no_punish(self, create_admin_logs):
        await create_admin_logs.propagate(MockedMessage().to_mock(), CorePayload())

    @pytest.mark.asyncio
    async def test_set_punish_types(self, create_admin_logs):
        with pytest.raises(GuildNotFound):
            await create_admin_logs.propagate(
                MockedMessage().to_mock(),
                CorePayload(
                    member_should_be_punished_this_message=True, member_was_banned=True
                ),
            )

        with pytest.raises(GuildNotFound):
            await create_admin_logs.propagate(
                MockedMessage().to_mock(),
                CorePayload(
                    member_should_be_punished_this_message=True, member_was_kicked=True
                ),
            )

        with pytest.raises(GuildNotFound):
            await create_admin_logs.propagate(
                MockedMessage().to_mock(),
                CorePayload(
                    member_should_be_punished_this_message=True, member_was_warned=True
                ),
            )
