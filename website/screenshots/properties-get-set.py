"""Get Property and Set Property in an operator: an add-on property (Count)
read, Blender's current frame set to it, the add-on's Status text set."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 440)


def setup():
    bpy.context.scene.sna.addon.addon_name = "Frame Tools"
    count = helpers.add_property("Start Frame", "INTEGER", default_int=12).id
    status = helpers.add_property("Status", "STRING").id
    tree = helpers.new_tree("Frame Tools")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    op = helpers.add_node(tree, "SNA_Node_Operator", (-560, 60))
    op.inputs["label"].value = "Go to Start"
    get = helpers.add_node(tree, "SNA_Node_GetProperty", (-560, -170))
    helpers.pick_property(get, helpers.prop(count))
    set_frame = helpers.add_node(tree, "SNA_Node_SetProperty", (-300, 60))
    set_frame.mode = "BLENDER"
    set_frame.path = "scene.frame_current"
    set_status = helpers.add_node(tree, "SNA_Node_SetProperty", (-50, 60))
    helpers.pick_property(set_status, helpers.prop(status))
    helpers.flush()
    set_status.socket("value").value = "Back at the start"
    link(op.outputs["Execute"], set_frame.inputs[0])
    link(get.outputs["Value"], set_frame.socket("value"))
    link(set_frame.outputs[0], set_status.inputs[0])
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=2)
