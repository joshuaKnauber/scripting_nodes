import bpy


def redraw(all: bool = False):
    """Redraws the UI."""
    if all:
        for area in bpy.context.screen.areas:
            area.tag_redraw()
    else:
        bpy.context.area.tag_redraw()
