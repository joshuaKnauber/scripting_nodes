"""A layout for the elements after a node, so settings on it (scale, state,
...) change only those: Blender applies a layout's settings to everything
in it, also what was drawn before, and the last value set wins."""


def sublayout(ctx):
    """(name, code creating it): a row inside a row, a column otherwise."""
    if ctx.horizontal:
        name = ctx.var("row")
        return name, f"{name} = {ctx.layout}.row()"
    name = ctx.var("col")
    return name, f"{name} = {ctx.layout}.column()"
