"""
LICENSE
The MIT License (MIT)

Copyright (c) 2020-2021 Skelmis

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
LICENSE
"""

import datetime

"""
Used to store a message object, essentially a glorified dictionary
"""


class Message:
    """Represents a lower level object needed to maintain messages"""

    __slots__ = [
        "_id",
        "_channel_id",
        "_guild_id",
        "_content",
        "_author_id",
        "_creation_time",
        "_is_duplicate",
    ]

    def __init__(self, id, content, author_id, channel_id, guild_id):
        """
        Set & store a smaller object footprint then a standard
        message object for memory purposes :)

        Parameters
        ==========
        id : int
            The id of the message
        content : String
            The actual message content
        author_id : int
            The author of said message
        channel_id : int
            The channel this message is in
        guild_id : int
            The guild this message belongs to

        Raises
        ======
        ValueError
            When an item is not the correct ignore_type for conversion

        Notes
        =====
        This enforces strict types by conversion and ignore_type checking
        pass through of the correct ignore_type is required.
        """
        self.id = int(id)
        self.content = str(content)
        self.author_id = int(author_id)
        self.channel_id = int(channel_id)
        self.guild_id = int(guild_id)
        self.is_duplicate = False
        self._creation_time = datetime.datetime.now(datetime.timezone.utc)

    def __repr__(self):
        return (
            f"'{self.__class__.__name__} object. Content: {self.content}, Message Id: {self.id}, "
            f"Author Id: {self.author_id}, Channel Id: {self.channel_id}, Guild Id: {self.guild_id} "
            f"Creation time: {self._creation_time}'"
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
            When the comparison object is not of ignore_type `Message`

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
            and self.author_id == other.author_id
            and self.channel_id == other.channel_id
            and self.guild_id == other.guild_id
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
        return hash((self.id, self.author_id, self.guild_id, self.channel_id))

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
    def author_id(self):
        return self._author_id

    @author_id.setter
    def author_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._author_id = value

    @property
    def channel_id(self):
        return self._channel_id

    @channel_id.setter
    def channel_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._channel_id = value

    @property
    def guild_id(self):
        return self._guild_id

    @guild_id.setter
    def guild_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Expected integer")
        self._guild_id = value

    @property
    def creation_time(self):
        return self._creation_time

    @creation_time.setter
    def creation_time(self, value):
        # We don't want creationTime changed
        return

    @property
    def is_duplicate(self):
        return self._is_duplicate

    @is_duplicate.setter
    def is_duplicate(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_duplicate should be a bool")

        self._is_duplicate = value
