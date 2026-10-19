"""Input values in a panel: Add-on Info and Current Time put into a label
with Format String."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _data_panel import TAB, hide_node_sidebar, panel  # noqa: E402

WINDOW_SIZE = (1200, 560)
LAYOUT = "split"
SIDEBAR_TAB = TAB
CROP = (0, 0, 0.855, 0.8)  # not the properties editor or timeline
FRAME = "corner"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("About")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    draw = panel(tree, (-220, 300), "About")
    info = add("SNA_Node_AddonInfo", -620, 100)
    time = add("SNA_Node_CurrentTime", -620, -80)
    time.inputs["Format"].value = "%d.%m.%Y"
    title = add("SNA_Node_FormatString", -420, 100)
    title.width = 180
    title.inputs["Format"].value = "{} {}"
    date = add("SNA_Node_FormatString", -420, -80)
    date.width = 180
    date.inputs["Format"].value = "Opened on {}"
    label = add("SNA_Node_Label", -20, 200)
    label.inputs["icon"].value = "INFO"
    label_2 = add("SNA_Node_Label", 180, 200)
    label_2.inputs["icon"].value = "TIME"
    link(info.outputs["Name"], title.inputs[-1])
    link(info.outputs["Version"], title.inputs[-1])
    link(time.outputs["Text"], date.inputs[-1])
    link(draw.outputs["Draw"], label.inputs[0])
    link(title.outputs[0], label.inputs["Label"])
    link(label.outputs[0], label_2.inputs[0])
    link(date.outputs[0], label_2.inputs["Label"])
    helpers.flush()
    return tree


def after(context):
    hide_node_sidebar(context)
