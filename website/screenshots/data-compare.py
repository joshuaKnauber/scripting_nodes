"""A panel label that changes with the selection: Compare on the number of
selected objects, Switch Data picks the text."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _data_panel import TAB, hide_node_sidebar, panel, select  # noqa: E402

WINDOW_SIZE = (1200, 560)
LAYOUT = "split"
SIDEBAR_TAB = TAB
CROP = (0, 0, 0.855, 0.8)  # not the properties editor or timeline
FRAME = "corner"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Selection Info"
    for name, location in (("Cone", (3, 0, 0)), ("Sphere", (-3, 0, 0))):
        if name not in bpy.data.objects:
            if name == "Cone":
                bpy.ops.mesh.primitive_cone_add(location=location)
            else:
                bpy.ops.mesh.primitive_uv_sphere_add(location=location)
            bpy.context.active_object.name = name
    select("Cube", "Sphere")
    tree = helpers.new_tree("Selection Info")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    draw = panel(tree, (-170, 320), "Selection")
    selected = add("SNA_Node_BlendData", -850, 0)
    selected.path_root = "CONTEXT"
    selected.path = "selected_objects"
    length = add("SNA_Node_ListLength", -580, 0)
    compare = add("SNA_Node_Compare", -400, 140)
    compare.comparison_type = ">"
    zero = add("SNA_Node_Integer", -580, 170)
    zero.value = 0
    text = add("SNA_Node_FormatString", -400, -60)
    text.width = 190
    text.inputs["Format"].value = "{} objects selected"
    switch = add("SNA_Node_SwitchData", -170, 60)
    switch.data_type = "ScriptingStringSocket"
    helpers.flush()
    switch.inputs["False"].value = "Nothing selected"
    label = add("SNA_Node_Label", 40, 200)
    label.inputs["icon"].value = "RESTRICT_SELECT_OFF"
    link(selected.outputs[0], length.inputs["List"])
    link(length.outputs[0], compare.inputs["A"])
    link(zero.outputs[0], compare.inputs["B"])
    link(length.outputs[0], text.inputs[-1])
    link(compare.outputs[0], switch.inputs["Condition"])
    link(text.outputs[0], switch.inputs["True"])
    link(draw.outputs["Draw"], label.inputs[0])
    link(switch.outputs[0], label.inputs["Label"])
    helpers.flush()
    return tree


def after(context):
    hide_node_sidebar(context)
