"""Three events: On Load (After) prints the file name, On Blender Change
reports a new active object, On Blender Close prints a goodbye."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, hide_node_sidebar  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 540)


def setup():
    bpy.context.scene.sna.addon.addon_name = "Scene Watcher"
    tree = helpers.new_tree("Events")
    load = add(tree, "SNA_Node_OnLoad", (-520, 260), when="load_post")
    loaded = add(tree, "SNA_Node_Print", (-260, 260))
    loaded.inputs["Text"].value = "A file was opened"
    change = add(tree, "SNA_Node_OnBlenderChange", (-600, 40))
    change.path_root = "CONTEXT"
    change.path = "view_layer.objects.active"
    changed = add(tree, "SNA_Node_Print", (-260, 40))
    changed.inputs["Text"].value = "The active object changed"
    close = add(tree, "SNA_Node_OnBlenderClose", (-520, -160))
    bye = add(tree, "SNA_Node_Print", (-260, -160))
    bye.inputs["Text"].value = "Goodbye"
    for event, printer in ((load, loaded), (change, changed), (close, bye)):
        helpers.link(tree, event.outputs[0], printer.inputs[0])
    return tree


def after(context):
    hide_node_sidebar(context)
