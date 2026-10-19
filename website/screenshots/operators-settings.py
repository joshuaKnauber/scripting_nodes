"""The Operator node's Settings popup: Invoke Type Properties Dialog with
its title and confirm button, and the Options."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, hide_node_sidebar, invoke_in  # noqa: E402

WINDOW_SIZE = (760, 660)
UI_SCALE = 1.25
AREA_ONLY = True
CROP = (0, 0, 0.55, 0.93)
FRAME = "right"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Cube Tools")
    op = add(tree, "SNA_Node_Operator", (0, 0))
    op.inputs["Label"].value = "Add Cubes"
    op.operator_description = "Add a row of cubes"
    op.invoke_type = "PROPS_DIALOG"
    op.dialog_title = "Add a Row of Cubes"
    op.dialog_confirm_text = "Add"
    helpers.flush()
    helpers.add_property("Count", "INTEGER", owner=op, default_int=5)
    return tree


def after(context):
    hide_node_sidebar(context)
    tree = bpy.data.node_groups["Cube Tools"]
    op = next(n for n in tree.nodes if n.bl_idname == "SNA_Node_Operator")
    invoke_in(
        context,
        "NODE_EDITOR",
        "sna.operator_node_settings",
        mouse=(0.06, 0.86),
        delay=1.0,
        node_id=op.id,
        show_options=True,
    )
