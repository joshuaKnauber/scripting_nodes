"""Blender Function nodes in an operator: create an empty object and link
it to the active collection."""

import os
import sys

import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 360)


def function(tree, location, root, path, name):
    node = helpers.add_node(tree, "SNA_Node_BlenderFunction", location)
    node.path_root = root
    node.path = path
    node.function = name
    return node


def setup():
    tree = helpers.new_tree("Object Tools")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    op = helpers.add_node(tree, "SNA_Node_Operator", (-600, 0))
    op.socket("label").value = "Add Marker"
    new = function(tree, (-370, 0), "DATA", "objects", "new")
    linker = function(tree, (-50, 0), "CONTEXT", "collection.objects", "link")
    helpers.flush()
    new.socket("param_name").value = "Marker"
    link(op.outputs["Execute"], new.inputs[0])
    link(new.outputs[0], linker.inputs[0])
    link(new.socket("param_object", output=True), linker.socket("param_object"))
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=1)
