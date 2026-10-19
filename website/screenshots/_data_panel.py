"""Shared bits of the Data screenshots: a sidebar panel in the 3D viewport
with a few objects selected."""

import bpy
import helpers

TAB = "Tools"


def panel(tree, location, label):
    node = helpers.add_node(tree, "SNA_Node_Panel", location)
    node.inputs["Label"].value = label
    node.panel_category = TAB
    return node


def select(*names):
    for obj in bpy.context.scene.objects:
        obj.select_set(obj.name in names)


def hide_node_sidebar(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
