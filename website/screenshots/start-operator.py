"""Start guide: an Operator node running Blender's Add Monkey."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _start_addon import build  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (900, 420)
ZOOM_OUT = 1


def setup():
    return build(with_panel=False)


def after(context):
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
