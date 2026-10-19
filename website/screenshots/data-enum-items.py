"""Enum Item nodes in a function that gives the items of an enum property,
drawn expanded in a panel."""

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

SHAPES = (
    ("Cube", "MESH_CUBE", "A box with six faces"),
    ("Sphere", "MESH_UVSPHERE", "A UV sphere"),
    ("Cone", "MESH_CONE", "A cone with a round base"),
)


def setup():
    bpy.context.scene.sna.addon.addon_name = "Shape Tools"
    function, _, group_output = helpers.new_function(
        "Shape Items", outputs=[("Items", "ScriptingListSocket")]
    )
    group_output.location = (250, 0)
    create = helpers.add_node(function, "SNA_Node_CreateList", (0, 0))
    for i, (name, icon, description) in enumerate(SHAPES):
        item = helpers.add_node(function, "SNA_Node_EnumItem", (-300, 200 - i * 170))
        item.name_prop = name
        item.description = description
        item.inputs["icon"].value = icon
        helpers.link(function, item.outputs[0], create.inputs[-1])
    helpers.link(function, create.outputs["list"], group_output.inputs[0])
    helpers.flush()
    prop = helpers.add_property("Shape", "ENUM", items_function=function)

    tree = helpers.new_tree("Interface")
    draw = panel(tree, (-300, 0), "Add Shape")
    menu = helpers.add_node(tree, "SNA_Node_EnumMenu", (0, 0))
    menu.expand = True
    helpers.pick_property(menu, helpers.prop(prop.id))
    helpers.link(tree, draw.outputs["Draw"], menu.inputs[0])
    helpers.flush()
    return function


def after(context):
    hide_node_sidebar(context)
