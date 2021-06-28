import attr


@attr.s
class CorePayload:
    # Per user things
    member_warn_count: int = attr.ib(default=0)
    member_kick_count: int = attr.ib(default=0)
    member_duplicate_count: int = attr.ib(default=0)
    member_status: str = attr.ib(default="Unknown")
    member_was_warned: bool = attr.ib(default=False)
    member_was_kicked: bool = attr.ib(default=False)
    member_was_banned: bool = attr.ib(default=False)
    member_should_be_punished_this_message: bool = attr.ib(default=False)

    # Per channel things
    # TODO Add per channel returns
