"""A Trigger node running a Print, after its button was clicked: the
message shows in the node editor."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, hide_node_sidebar, invoke_in  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (800, 400)

_state = {}


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Testing")
    trigger = add(tree, "SNA_Node_Trigger", (-300, 0))
    printer = add(tree, "SNA_Node_Print", (-60, 0))
    printer.inputs["Text"].value = "Hello from the Trigger"
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    _state["trigger"] = trigger
    return tree


def after(context):
    hide_node_sidebar(context)
    idname = _state["trigger"].operator_idname
    invoke_in(context, "NODE_EDITOR", idname, delay=2.0)
