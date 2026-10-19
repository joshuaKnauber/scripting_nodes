"""A tree calling three functions: Greet (flow), Header (UI), Double (value)."""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _demo  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 560)


def setup():
    tree, _ = _demo.build()
    # closer together than the shared demo, so the nodes stay readable
    for node in tree.nodes:
        node.location = (node.location.x * 0.7, node.location.y * 0.6)
    return tree


def after(context):
    for tree in bpy.data.node_groups:
        for node in tree.nodes:
            node.select = False
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
