from antispam.exceptions import MemberNotFound, GuildNotFound


class UserTracking:
    """A simple class used to track users in guilds"""

    def __init__(self):
        self.data = {}

    def _get_guild(self, guild_id: int) -> dict:
        """
        Returns the given guild's data

        Parameters
        ----------
        guild_id : int
            The guild to get data for

        Returns
        -------
        dict
            This guilds data

        Raises
        ------
        GuildNotFound
            This guild could not be found
        """
        if guild_id not in self.data:
            raise GuildNotFound

        return self.data[guild_id]

    def get_user(self, guild_id: int, user_id: int) -> dict:
        """
        Returns the given data for a stored user

        Parameters
        ----------
        guild_id : int
            The guild for the user we want
        user_id : int
            The user we want to get data for

        Returns
        -------
        dict
            A dictionary of stored data on this user

        Raises
        ------
        UserNotFound
            The given user/guild could not be found internally
        """
        try:
            guild = self._get_guild(guild_id=guild_id)
        except GuildNotFound:
            raise MemberNotFound

        if user_id not in guild:
            raise MemberNotFound

        return guild[user_id]

    def set_user(self, guild_id: int, user_id: int, user_data: dict) -> None:
        """
        Stores a user's data within a guild

        Parameters
        ----------
        guild_id : int
            The guild to add this user's
            data into
        user_id : int
            The user's id to store
        user_data : dict
            The data to store
        """
        try:
            self._get_guild(guild_id=guild_id)
        except GuildNotFound:
            self.data[guild_id] = {}

        self.data[guild_id][user_id] = user_data
