"""String nodes drawn in a panel: Format String with a padded number, and
Split String joined again with Join List and Change Case."""

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
    bpy.context.scene.sna.addon.addon_name = "Render Tools"
    tree = helpers.new_tree("Text")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    draw = panel(tree, (-240, 320), "Output")
    number = add("SNA_Node_Integer", -700, 120)
    number.value = 7
    pad = add("SNA_Node_PadString", -520, 140)
    file_name = add("SNA_Node_FormatString", -320, 120)
    file_name.width = 170
    file_name.inputs["Format"].value = "Shot_{}.png"
    split = add("SNA_Node_SplitString", -700, -100)
    split.width = 170
    split.inputs["String"].value = "red green blue"
    join = add("SNA_Node_JoinList", -500, -100)
    join.inputs["Separator"].value = " / "
    case = add("SNA_Node_ChangeCase", -320, -100)
    case.case = "title"
    label = add("SNA_Node_Label", -40, 220)
    label.inputs["icon"].value = "FILE_IMAGE"
    label_2 = add("SNA_Node_Label", 160, 220)
    label_2.inputs["icon"].value = "COLOR"
    link(number.outputs[0], pad.inputs["String"])
    link(pad.outputs[0], file_name.inputs[-1])
    link(split.outputs[0], join.inputs["List"])
    link(join.outputs[0], case.inputs["String"])
    link(draw.outputs["Draw"], label.inputs[0])
    link(file_name.outputs[0], label.inputs["Label"])
    link(label.outputs[0], label_2.inputs[0])
    link(case.outputs[0], label_2.inputs["Label"])
    helpers.flush()
    return tree


def after(context):
    hide_node_sidebar(context)
