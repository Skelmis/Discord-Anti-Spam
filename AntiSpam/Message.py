"""
Used to store a message object, essentially a glorified dictionary
"""


class Message:
    __slots__ = ["_id", "_channelId", "_guildId", "_content", "_authorId"]

    def __init__(self, id, content, authorId, channelId, guildId):
        """
        Set & store a smaller object footprint then a standard
        message object for memory purposes :)

        Parameters
        ==========
        id : int
            The id of the message
        content : String
            The actual message content
        authorId : int
            The author of said message
        channelId : int
            The channel this message is in
        guildId : int
            The guild this message belongs to

        Raises
        ======
        ValueError
            When an item is not the correct type for conversion

        Notes
        =====
        This enforces strict types by conversion and type checking
        pass through of the correct type is required.
        """
        self.id = int(id)
        self.content = str(content)
        self.authorId = int(authorId)
        self.channelId = int(channelId)
        self.guildId = int(guildId)

    def __repr__(self):
        return f"{self.__class__.__name__} object"

    def __str__(self):
        return f"{self.__class__.__name__} object - '{self.content}'"

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._id = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        try:
            self._content = str(value)
        except ValueError:
            raise ValueError("Expected String")

    @property
    def authorId(self):
        return self._authorId

    @authorId.setter
    def authorId(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._authorId = value

    @property
    def channelId(self):
        return self._channelId

    @channelId.setter
    def channelId(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._channelId = value

    @property
    def guildId(self):
        return self._guildId

    @guildId.setter
    def guildId(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._guildId = value
