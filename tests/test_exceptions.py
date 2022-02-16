# noinspection PyUnresolvedReferences,PyPackageRequirements
from antispam import (
    BaseASHException,
    DuplicateObject,
    GuildAddonNotFound,
    GuildNotFound,
    InvalidMessage,
    LogicError,
    MemberAddonNotFound,
    MemberNotFound,
    MissingGuildPermissions,
    NotFound,
    ObjectMismatch,
    PluginError,
)


class TestExceptions:
    def test_base(self):
        assert (
            str(BaseASHException()) == "A base exception handler for the ASH ecosystem."
        )

    def test_base_init(self):
        assert str(BaseASHException("test")) == "test"

    def test_duplicate_object(self):
        assert (
            str(DuplicateObject())
            == "Raised because you attempted to create and add an object, using the exact "
            "same id's as a pre-existing one."
        )

    def test_object_mismatch(self):
        assert (
            str(ObjectMismatch())
            == "Raised because you attempted add a message to a member, but that member didn't create that message."
        )

    def test_logic_error(self):
        assert (
            str(LogicError())
            == "Raised because internal logic has failed. Please create an issue in the github and include traceback."
        )

    def test_missing_guild_perms(self):
        assert (
            str(MissingGuildPermissions())
            == "I need both permissions to kick & ban people from this guild in order to work!"
        )

    def test_not_found(self):
        assert str(NotFound()) == "Something could not be found."

    def test_member_not_found(self):
        assert (
            str(MemberNotFound())
            == "A Member matching this id and guild id could not be found in the cache."
        )

    def test_member_addon_not_found(self):
        assert (
            str(MemberAddonNotFound())
            == "This class has no addon stored on this member."
        )

    def test_guild_not_found(self):
        assert (
            str(GuildNotFound())
            == "A Guild matching this guild id could not be found in the cache."
        )

    def test_guild_addon_not_found(self):
        assert (
            str(GuildAddonNotFound())
            == "This class has not addon stored on this guild."
        )

    def test_extension_error(self):
        assert (
            str(PluginError())
            == "An error occurred that was related to a plugin and not AntiSpamHandler"
        )

    def test_invalid_message(self):
        assert (
            str(InvalidMessage())
            == "Could not create a use-able message for the given message."
        )
