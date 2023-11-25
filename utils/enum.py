_item_map = {}


def make_enum_item(value: str, name: str, descr: str, preview_id: int, id: int):
    """Create a new enum item that doesn't break in an items function."""
    global _item_map
    lookup = (
        str(id)
        + "\\0"
        + str(name)
        + "\\0"
        + str(descr)
        + "\\0"
        + str(preview_id)
        + "\\0"
        + str(id)
    )
    if not lookup in _item_map:
        _item_map[lookup] = (value, name, descr, preview_id, id)
    return _item_map[lookup]
