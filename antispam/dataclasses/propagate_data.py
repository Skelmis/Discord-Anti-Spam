import attr


@attr.s(slots=True)
class PropagateData:
    """A simplistic dataclass representing the data propagate needs"""

    guild_id: int = attr.ib()
    member_name: str = attr.ib()
    member_id: int = attr.ib()

    has_perms_to_make_guild: bool = attr.ib()
