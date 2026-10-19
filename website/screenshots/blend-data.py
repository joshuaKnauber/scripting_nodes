"""Blender Data nodes in an operator: the active object's Bevel width (by
name) and the vertex count of its mesh, printed."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 520)


def blend_data(tree, location, path, root="CONTEXT"):
    node = helpers.add_node(tree, "SNA_Node_BlendData", location)
    node.path_root = root
    node.path = path
    return node


def setup():
    cube = bpy.data.objects.get("Cube")
    if cube is not None and "Bevel" not in cube.modifiers:
        cube.modifiers.new("Bevel", "BEVEL")
    tree = helpers.new_tree("Object Report")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    op = helpers.add_node(tree, "SNA_Node_Operator", (-620, 220))
    op.socket("label").value = "Report"

    active = blend_data(tree, (-620, 0), "active_object")
    bevel = blend_data(tree, (-330, 0), "modifiers[].width", root="INPUT")
    bevel.path_keys[0].mode = "NAME"
    bevel.socket("key_0").value = "Bevel"
    link(active.outputs[0], bevel.socket("data"))
    mesh = blend_data(tree, (-620, -200), "active_object.data")
    mesh.path_cast = "Mesh"
    vertices = blend_data(tree, (-330, -200), "vertices", root="INPUT")
    link(mesh.outputs[0], vertices.socket("data"))
    length = helpers.add_node(tree, "SNA_Node_CollectionLength", (-40, -170))

    link(vertices.outputs[0], length.inputs[0])
    print_width = helpers.add_node(tree, "SNA_Node_Print", (-40, 220))
    print_count = helpers.add_node(tree, "SNA_Node_Print", (180, 220))
    link(op.outputs["Execute"], print_width.inputs[0])
    link(bevel.outputs[0], print_width.inputs[1])
    link(print_width.outputs[0], print_count.inputs[0])
    link(length.outputs[0], print_count.inputs[1])
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=3)
