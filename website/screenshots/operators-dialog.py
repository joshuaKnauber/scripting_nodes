"""The dialog of an operator with Invoke Type Properties Dialog: a title,
its Count and Size properties and an Add button, open in the 3D Viewport."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, invoke_in  # noqa: E402

WINDOW_SIZE = (900, 560)
AREA_ONLY = True
UI_SCALE = 1.25
FRAME = "float"

_state = {}


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Cube Rows")
    op = add(tree, "SNA_Node_Operator", (0, 0))
    op.inputs["Label"].value = "Add Cubes"
    op.invoke_type = "PROPS_DIALOG"
    op.dialog_title = "Add a Row of Cubes"
    op.dialog_confirm_text = "Add"
    helpers.flush()
    helpers.add_property("Count", "INTEGER", owner=op, default_int=5)
    helpers.add_property("Size", "FLOAT", owner=op, default_float=0.5)
    helpers.add_property("Random Rotation", "BOOLEAN", owner=op)
    _state["op"] = op.operator_idname
    return None  # keep the 3D Viewport


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.show_region_ui = False
    invoke_in(context, "VIEW_3D", _state["op"], mouse=(0.5, 0.55), delay=1.0)
