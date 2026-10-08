"""Inside a function: Group Input / Output and the native "Group" sidebar tab
with the function's parameters and return values."""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _functions_demo  # noqa: E402

SIDEBAR_TAB = "Group"
ZOOM_OUT = 1


def setup():
    _, functions = _functions_demo.build()
    greet = functions["Greet"]
    greet.interface.active_index = 1
    return greet


def after(context):
    bpy.context.scene.sna.dev.show_node_code = False
