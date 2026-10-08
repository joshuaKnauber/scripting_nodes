"""A tree calling three functions: Greet (flow), Header (UI), Double (value)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _demo  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1150, 640)


def setup():
    tree, _ = _demo.build()
    return tree


def after(context):
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
