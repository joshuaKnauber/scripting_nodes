from uuid import uuid4


def get_short_id():
    """Returns a unique id"""
    return uuid4().hex[:5].upper()
