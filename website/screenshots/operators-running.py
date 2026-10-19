"""Run Operator in both modes: Blender's Shade Smooth, then the add-on's
own Rename Objects operator with its Prefix set and Invoke Default."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, blender_operator, hide_node_sidebar  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1100, 520)


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Tidy Up")
    rename = add(tree, "SNA_Node_Operator", (-560, 330))
    rename.inputs["Label"].value = "Rename Objects"
    rename.invoke_type = "PROPS_DIALOG"
    helpers.flush()
    helpers.add_property("Prefix", "STRING", owner=rename, default_string="Obj_")

    tidy = add(tree, "SNA_Node_Operator", (-560, 60))
    tidy.inputs["Label"].value = "Tidy Up"
    smooth = add(tree, "SNA_Node_RunOperator", (-330, 60), mode="BLENDER")
    smooth.operator_blender = blender_operator("object.shade_smooth")
    run = add(tree, "SNA_Node_RunOperator", (-80, 60))
    helpers.point(run, "operator_sn", rename)
    run.exec_context = "INVOKE_DEFAULT"
    helpers.flush()
    smooth.width = run.width = 210
    run.socket("arg_prefix").value = "Prop_"
    helpers.link(tree, tidy.outputs["Execute"], smooth.inputs[0])
    helpers.link(tree, smooth.outputs[0], run.inputs[0])
    return tree


def after(context):
    hide_node_sidebar(context)
