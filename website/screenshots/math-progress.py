"""Map Range turns the current frame into a 0 to 1 factor for a Progress
bar; Format String shows it as a percentage."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _data_panel import TAB, hide_node_sidebar, panel  # noqa: E402

WINDOW_SIZE = (1200, 560)
LAYOUT = "split"
SIDEBAR_TAB = TAB
CROP = (0, 0, 0.855, 0.8)  # not the properties editor or timeline
FRAME = "corner"


def blend_data(tree, location, path):
    node = helpers.add_node(tree, "SNA_Node_BlendData", location)
    node.path_root = "CONTEXT"
    node.path = path
    return node


def setup():
    bpy.context.scene.sna.addon.addon_name = "Playback"
    bpy.context.scene.frame_end = 120
    bpy.context.scene.frame_current = 84
    tree = helpers.new_tree("Playback")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    draw = panel(tree, (-240, 320), "Playback")
    frame = blend_data(tree, (-700, 180), "scene.frame_current")
    start = blend_data(tree, (-700, 20), "scene.frame_start")
    end = blend_data(tree, (-700, -140), "scene.frame_end")
    map_range = helpers.add_node(tree, "SNA_Node_MapRange", (-440, 120))
    map_range.inputs["New Max"].value = 1.0
    percent = helpers.add_node(tree, "SNA_Node_FormatString", (-240, 0))
    percent.width = 190
    percent.inputs["Format"].value = "{:.0%} played"
    progress = helpers.add_node(tree, "SNA_Node_Progress", (-40, 220))
    link(frame.outputs[0], map_range.inputs["Value"])
    link(start.outputs[0], map_range.inputs["Old Min"])
    link(end.outputs[0], map_range.inputs["Old Max"])
    link(map_range.outputs["Float Result"], progress.inputs["Factor"])
    link(map_range.outputs["Float Result"], percent.inputs[-1])
    link(percent.outputs[0], progress.inputs["Text"])
    link(draw.outputs["Draw"], progress.inputs[0])
    helpers.flush()
    return tree


def after(context):
    hide_node_sidebar(context)
