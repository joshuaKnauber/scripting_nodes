"""The panel the properties demo draws in the 3D viewport sidebar."""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _properties  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (900, 420)


def setup():
    _properties.build()
    # open the sidebar early: its tabs only exist once it has drawn
    for area in bpy.context.window_manager.windows[0].screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.show_region_ui = True
    return None  # keep the 3D viewport
