"""On Property Update: when the add-on's Shot Length changes, the scene's
End Frame is set to it."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

AREA_ONLY = True
ZOOM_OUT = 2
WINDOW_SIZE = (900, 300)


def setup():
    bpy.context.scene.sna.addon.addon_name = "Shot Tools"
    length = helpers.add_property("Shot Length", "INTEGER", default_int=120).id
    tree = helpers.new_tree("Shot Tools")
    update = helpers.add_node(tree, "SNA_Node_OnPropertyUpdate", (-300, 0))
    helpers.pick_property(update, helpers.prop(length))
    end = helpers.add_node(tree, "SNA_Node_SetProperty", (-40, 0))
    end.mode = "BLENDER"
    end.path = "scene.frame_end"
    helpers.flush()
    helpers.link(tree, update.outputs[0], end.inputs[0])
    helpers.link(tree, update.outputs["Value"], end.socket("value"))
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=0)
