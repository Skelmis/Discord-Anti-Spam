import datetime

import attr


@attr.s(frozen=True, slots=True)
class SubstituteArgs:
    member_id: int = attr.ib()
    member_name: str = attr.ib()
    member_avatar: str = attr.ib()
    bot_id: int = attr.ib()
    bot_name: str = attr.ib()
    bot_avatar: str = attr.ib()
    guild_id: int = attr.ib()
    guild_name: str = attr.ib()
    guild_icon: str = attr.ib()

    @property
    def mention_member(self) -> str:
        return f"<@{self.member_id}>"

    @property
    def mention_bot(self) -> str:
        return f"<@{self.bot_id}>"

    @property
    def timestamp_now(self) -> str:
        return datetime.datetime.now().strftime("%I:%M:%S %p, %d/%m/%Y")

    @property
    def timestamp_today(self) -> str:
        return datetime.datetime.now().strftime("%d/%m/%Y")
