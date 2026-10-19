"""A sidebar panel showing the current mode and, with Is Object Type, a
different line for meshes and other objects."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

WINDOW_SIZE = (1400, 700)
LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"
CROP = (0, 0, 0.835, 0.84)
FRAME = "corner"


def setup():
    tree = helpers.new_tree("Object Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    panel = add("SNA_Node_Panel", -650, 0)
    panel.socket("label").value = "Object Tools"
    panel.panel_category = "Object Tools"
    mode = add("SNA_Node_IsInMode", -650, -190)
    mode_label = add("SNA_Node_Label", -420, 0)
    active = add("SNA_Node_BlendData", -700, -320)
    active.path = "active_object"
    is_mesh = add("SNA_Node_IsObjectType", -420, -250)
    branch = add("SNA_Node_IfElse", -200, 0)
    mesh_label = add("SNA_Node_Label", 20, 60)
    mesh_label.socket("text").value = "Mesh tools ready"
    other_label = add("SNA_Node_Label", 20, -140)
    other_label.socket("text").value = "Select a mesh"
    link(panel.outputs["Draw"], mode_label.inputs[0])
    link(mode.socket("mode", output=True), mode_label.socket("text"))
    link(mode_label.outputs[0], branch.inputs[0])
    link(active.outputs[0], is_mesh.inputs[0])
    link(is_mesh.outputs[0], branch.socket("condition"))
    link(branch.socket("then", output=True), mesh_label.inputs[0])
    link(branch.socket("else", output=True), other_label.inputs[0])
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=1)
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.show_region_ui = True
    bpy.context.view_layer.objects.active = bpy.data.objects.get("Cube")
