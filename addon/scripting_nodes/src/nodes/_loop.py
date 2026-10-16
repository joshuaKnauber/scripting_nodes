"""The `for` line of the For Each nodes: loop variables nothing uses are
`_`, without an index there's no `enumerate()`."""


def for_each(ctx, items: str):
    """(`for ... in ...:` line, {output key: variable}) for looping over
    `items`, with the node's Item and Index outputs."""
    item = ctx.var("item") if ctx.is_linked("item") else "_"
    if ctx.is_linked("index"):
        index = ctx.var("index")
        return f"for {index}, {item} in enumerate({items}):", {
            "item": item,
            "index": index,
        }
    return f"for {item} in {items}:", {"item": item}
