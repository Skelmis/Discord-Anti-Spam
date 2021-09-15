from antispam.abc import Cache


class RedisCache(Cache):
    """Not implemented lol"""

    def __init__(self, handler):
        self.handler = handler

        raise NotImplementedError
