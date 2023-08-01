import math
from typing import Tuple

import blf
import bpy

from ....utils.is_serpens import in_sn_tree

_node_times = {}  # times in milliseconds
_node_errors = {}


def set_node_time(id: str, time: int):
    """ Sets the time the node took to run """
    global _node_times
    _node_times[id] = time
    bpy.context.area.tag_redraw()


def set_node_error(id: str, error: str):
    """ Sets the nodes error message """
    global _node_errors
    _node_errors[id] = error
    for a in bpy.context.screen.areas:
        if a.type == "NODE_EDITOR":
            a.tag_redraw()


def get_node_top_left(node: bpy.types.Node) -> Tuple[float, float]:
    x = node.location[0]
    y = node.location[1]
    for region in bpy.context.area.regions:
        if region.type == "WINDOW":
            ui_scale = bpy.context.preferences.system.ui_scale
            return region.view2d.view_to_region(x*ui_scale, y*ui_scale, clip=False)
    return (x, y)


def get_zoom_level():
    ui_scale = bpy.context.preferences.system.ui_scale
    for region in bpy.context.area.regions:
        if region.type == "WINDOW":
            test_length = 1000
            x0, y0 = region.view2d.view_to_region(0, 0, clip=False)
            x1, y1 = region.view2d.view_to_region(test_length, test_length, clip=False)
            xl = x1 - x0
            yl = y1 - y0
            return (math.sqrt(xl**2 + yl**2) / test_length) * ui_scale
    return 1 * ui_scale


def draw_node_overlays():
    """ Draws node details to the interface """
    if not in_sn_tree(bpy.context):
        return
    zoom = get_zoom_level()
    blf.size(0, 12*zoom)
    for node in bpy.context.space_data.node_tree.nodes:
        if node.id in _node_times:
            x, y = get_node_top_left(node)
            blf.position(0, x, y, 0)
            blf.draw(0, f"{round(_node_times[node.id], 1)} ms")
