"""
The MIT License (MIT)

Copyright (c) 2020 Skelmis

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import datetime

"""
Used to store a message object, essentially a glorified dictionary
"""


class Message:
    """Represents a lower level object needed to maintain messages

    """

    __slots__ = [
        "_id",
        "_channelId",
        "_guildId",
        "_content",
        "_authorId",
        "_creationTime",
        "_isDuplicate",
    ]

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
        self.isDuplicate = False
        self._creationTime = datetime.datetime.now(datetime.timezone.utc)

    def __repr__(self):
        return (
            f"'{self.__class__.__name__} object. Content: {self.content}, Message Id: {self.id}, "
            f"Author Id: {self.authorId}, Channel Id: {self.channelId}, Guild Id: {self.guildId} "
            f"Creation time: {self._creationTime}'"
        )

    def __str__(self):
        return f"{self.__class__.__name__} object - '{self.content}'"

    def __eq__(self, other):
        """
        This is called with a 'obj1 == obj2' comparison object is made

        Checks everything besides message content to figure out if a message
        is the same or not

        Parameters
        ----------
        other : Message
            The object to compare against

        Returns
        -------
        bool
            `True` or `False` depending on whether they are the same or not

        Raises
        ======
        ValueError
            When the comparison object is not of type `Message`

        Notes
        =====
        Does not check creation time, because that can be different
        and this is mainly used to ensure we don't create duplicates
        and creation time is this class's time not the message's time
        """
        if not isinstance(other, Message):
            raise ValueError

        if (
            self.id == other.id
            and self.authorId == other.authorId
            and self.channelId == other.channelId
            and self.guildId == other.guildId
        ):
            return True
        return False

    def __hash__(self):
        """
        Given we create a __eq__ dunder method, we also needed
        to create one for __hash__ lol

        Returns
        -------
        int
            The hash of all id's
        """
        return hash((self.id, self.authorId, self.guildId, self.channelId))

    @property
    def id(self):
        """
        The `getter` method
        """
        return self._id

    @id.setter
    def id(self, value):
        """
        The `setter` method
        """
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

    @property
    def creationTime(self):
        return self._creationTime

    @creationTime.setter
    def creationTime(self, value):
        # We don't want creationTime changed
        return

    @property
    def isDuplicate(self):
        return self._isDuplicate

    @isDuplicate.setter
    def isDuplicate(self, value):
        if not isinstance(value, bool):
            raise ValueError("isDuplicate should be a bool")

        self._isDuplicate = value
