"""A Preferences node with two properties (sidebar Node tab) drawn by a
Checkbox and a Number Field."""

import bpy
import helpers

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _interface_tools as tools  # noqa: E402

WINDOW_SIZE = (1200, 600)
AREA_ONLY = True
SIDEBAR_TAB = "Node"
FRAME = "float"
ZOOM_OUT = 5


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Preferences")
    prefs = tools.add(tree, "SNA_Node_Preferences", (-300, 0))
    tips = helpers.add_property("Show Tips", "BOOLEAN", owner=prefs)
    tips_id = tips.id
    count = helpers.add_property("Default Count", "INTEGER", owner=prefs, default_int=5)
    count_id = count.id
    checkbox = tools.add(tree, "SNA_Node_Checkbox", (-60, 110))
    number = tools.add(tree, "SNA_Node_NumberField", (-60, -110))
    helpers.flush()
    helpers.link(tree, prefs.outputs["Draw"], checkbox.inputs[0])
    helpers.link(tree, checkbox.outputs[0], number.inputs[0])
    helpers.pick_property(checkbox, helpers.prop(tips_id))
    helpers.pick_property(number, helpers.prop(count_id))
    for node in tree.nodes:
        node.select = False
    prefs.select = True
    tree.nodes.active = prefs
    return tree
