"""Flows and sockets: an operator (Logic) running a Print (Program), a panel
(Interface) drawing a label, both using the same value nodes."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _concepts_graph import build  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 640)


def setup():
    return build()


def after(context):
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
