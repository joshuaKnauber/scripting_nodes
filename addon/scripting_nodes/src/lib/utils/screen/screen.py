import bpy


def redraw_all():
    for area in bpy.context.screen.areas:
        area.tag_redraw()
