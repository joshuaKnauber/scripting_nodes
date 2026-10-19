"""An Operator node that adds a small cube and reports it, run by a button
in a sidebar panel, next to the panel in the 3D Viewport."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, blender_operator, hide_node_sidebar  # noqa: E402

WINDOW_SIZE = (1250, 640)
LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"
CROP = (0, 0, 0.86, 0.86)
FRAME = "corner"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Cube Tools")
    op = add(tree, "SNA_Node_Operator", (-560, 60))
    op.inputs["Label"].value = "Add Small Cube"
    run = add(tree, "SNA_Node_RunOperator", (-330, 60), mode="BLENDER")
    run.operator_blender = blender_operator("mesh.primitive_cube_add")
    helpers.flush()
    run.width = 200
    run.socket("arg_size").value = 0.5
    report = add(tree, "SNA_Node_Report", (-90, 60))
    report.inputs["Message"].value = "Added a small cube"
    helpers.link(tree, op.outputs["Execute"], run.inputs[0])
    helpers.link(tree, run.outputs[0], report.inputs[0])

    panel = add(tree, "SNA_Node_Panel", (-560, 300))
    panel.inputs["Label"].value = "Object Tools"
    panel.panel_category = "Object Tools"
    button = add(tree, "SNA_Node_Button", (-330, 300))
    helpers.point(button, "operator_sn", op)
    helpers.flush()
    button.inputs["icon"].value = "MESH_CUBE"
    helpers.link(tree, panel.outputs["Draw"], button.inputs[0])
    return tree


def after(context):
    hide_node_sidebar(context)
