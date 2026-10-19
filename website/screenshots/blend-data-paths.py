"""A panel drawing Blender properties by path: a checkbox and number fields
in Blender mode, one set up from a pasted data path."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

WINDOW_SIZE = (1500, 760)
CROP = (0, 0, 0.87, 0.8)
FRAME = "corner"
LAYOUT = "split"
SIDEBAR_TAB = "Render Tools"


def setup():
    cube = bpy.data.objects.get("Cube")
    if cube is not None and "Bevel" not in cube.modifiers:
        cube.modifiers.new("Bevel", "BEVEL")
    tree = helpers.new_tree("Render Tools")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-760, 0))
    panel.socket("label").value = "Render Tools"
    panel.panel_category = "Render Tools"
    simplify = helpers.add_node(tree, "SNA_Node_Checkbox", (-560, 0))
    simplify.mode = "BLENDER"
    simplify.path = "scene.render.use_simplify"
    frame_end = helpers.add_node(tree, "SNA_Node_NumberField", (-330, 0))
    frame_end.mode = "BLENDER"
    frame_end.path = "scene.frame_end"
    bevel = helpers.add_node(tree, "SNA_Node_NumberField", (-100, 0))
    bevel.mode = "BLENDER"
    bevel.paste_path('bpy.data.objects["Cube"].modifiers["Bevel"].width')
    link(panel.outputs["Draw"], simplify.inputs[0])
    link(simplify.socket("next", output=True), frame_end.inputs[0])
    link(frame_end.socket("next", output=True), bevel.inputs[0])
    helpers.flush()
    return tree


def after(context):
    # the node editor's sidebar would cover the nodes
    _blend_data_zoom.zoom_in(context, steps=1)
