"""Start guide result: the nodes next to the Monkeys panel in the 3D
viewport's sidebar, after the button added a monkey."""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _start_addon import build  # noqa: E402

WINDOW_SIZE = (1400, 800)
LAYOUT = "split"
SIDEBAR_TAB = "Monkey Tools"
CROP = (0, 0, 0.815, 0.78)
FRAME = "corner"


def setup():
    for obj in list(bpy.data.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj)
    return build()


def after(context):
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
    bpy.ops.monkey_tools.add_monkey()
