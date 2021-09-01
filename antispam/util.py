import datetime


def get_aware_time() -> datetime.datetime:
    """Used to get an aware datetime"""
    return datetime.datetime.now(datetime.timezone.utc)
