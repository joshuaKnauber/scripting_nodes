"""Custom properties: an operator tags the active object with
made_by = "Object Tools" and prints whether it has the tag."""

import os
import sys

import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 560)


def setup():
    tree = helpers.new_tree("Object Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    op = add("SNA_Node_Operator", -560, 80)
    op.inputs["label"].value = "Tag Object"
    active = add("SNA_Node_BlendData", -600, -330)
    active.path = "active_object"
    tag = add("SNA_Node_SetCustomProperty", -240, 80)
    tag.inputs["Name"].value = "made_by"
    value = add("SNA_Node_String", -560, -190)
    value.value = "Object Tools"
    get = add("SNA_Node_GetCustomProperty", -240, -260)
    get.inputs["Name"].value = "made_by"
    report = add("SNA_Node_Print", 20, 80)
    helpers.flush()
    link(op.outputs["Execute"], tag.inputs[0])
    link(active.outputs[0], tag.socket("data"))
    link(active.outputs[0], get.socket("data"))
    link(value.outputs[0], tag.socket("value"))
    link(tag.outputs[0], report.inputs[0])
    link(get.socket("exists", output=True), report.inputs[1])
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=2)
