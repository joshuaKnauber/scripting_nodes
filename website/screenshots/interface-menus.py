"""A Menu button and an Operator Menu dropdown in the Object Tools panel,
next to their nodes."""

import os
import sys

import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _interface_tools as tools  # noqa: E402

WINDOW_SIZE = (1200, 560)
LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"
FRAME = "corner"
CROP = (0, 0, 0.84, 0.86)


def setup():
    import bpy

    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    panel = tools.add(tree, "SNA_Node_Panel", (-560, 0))
    panel.inputs["Label"].value = "Object Tools"
    menu = tools.add(tree, "SNA_Node_Menu", (-390, 0))
    smooth = tools.button(tree, (-200, 200), "object.shade_smooth", "Smooth", "MOD_SMOOTH")
    flat = tools.button(tree, (-40, 200), "object.shade_flat", "Flat", "MESH_CUBE")
    modes = tools.add(tree, "SNA_Node_OperatorMenu", (-200, -120), mode="BLENDER")
    modes.operator_blender = tools.blender_operator("object.mode_set")
    helpers.flush()
    modes.enum_property = "mode"
    helpers.flush()
    menu.inputs["Label"].value = "Shading"
    menu.inputs["Icon"].value = "SHADING_RENDERED"
    modes.inputs["Label"].value = "Mode"
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(panel.outputs["Draw"], menu.inputs[0])
    link(menu.outputs["Menu"], smooth.inputs[0])
    link(smooth.outputs[0], flat.inputs[0])
    link(menu.outputs["After"], modes.inputs[0])
    return tree


def after(context):
    tools.hide_node_sidebar(context)
