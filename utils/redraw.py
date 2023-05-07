import bpy


def redraw(all=False):
    if all:
        for area in bpy.context.screen.areas:
            area.tag_redraw()
    else:
        bpy.context.area.tag_redraw()
