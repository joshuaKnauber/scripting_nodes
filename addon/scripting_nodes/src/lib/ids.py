from uuid import uuid4


def get_short_id():
    """A unique id for nodes and trees. Used in generated identifiers."""
    return uuid4().hex[:10].upper()
