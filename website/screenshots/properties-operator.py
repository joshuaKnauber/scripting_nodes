"""An Operator node's own properties: listed on the node, edited in the
sidebar's Node tab while it's selected."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 900)
SIDEBAR_TAB = "Node"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    op = helpers.add_node(tree, "SNA_Node_Operator", (0, 0))
    op.inputs["label"].value = "Scatter Objects"
    helpers.add_property("Count", "INTEGER", owner=op, default_int=10)
    helpers.add_property(
        "Radius",
        "FLOAT",
        owner=op,
        default_float=2.0,
        subtype_float="DISTANCE",
        unit="LENGTH",
    )
    helpers.add_property("Random Rotation", "BOOLEAN", owner=op, default_bool=True)
    op.active_property = 1
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=2, hide_sidebar=False)
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            nodes = area.spaces.active.node_tree.nodes
            nodes[0].select = True
            nodes.active = nodes[0]
