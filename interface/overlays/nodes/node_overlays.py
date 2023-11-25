import math
import os
from typing import Tuple

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ....utils.is_serpens import in_sn_tree

_node_times = {}  # times in milliseconds
_node_errors = {}

_monospace_font_id = 0


def get_monospace_font() -> int:
    """Loads the blender monospace font if not already loaded and returns the id"""
    global _monospace_font_id
    if not _monospace_font_id:
        font_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "assets",
            "fonts",
            "DejaVuSansMono.woff2",
        )
        _monospace_font_id = blf.load(font_path)
    return _monospace_font_id


def set_node_time(id: str, time: int):
    """Sets the time the node took to run"""
    global _node_times
    _node_times[id] = time
    bpy.context.area.tag_redraw()


def set_node_error(id: str, error: str):
    """Sets the nodes error message"""
    global _node_errors
    _node_errors[id] = error
    for a in bpy.context.screen.areas:
        if a.type == "NODE_EDITOR":
            a.tag_redraw()


def get_node_error_msg(node: bpy.types.Node):
    """Returns a formatted error message for this node"""
    global _node_errors
    if not node.id in _node_errors:
        return ""
    elif not _node_errors[node.id]:
        return ""
    return f"Node '{node.name}': {_node_errors[node.id]}"


def ui_scale():
    return bpy.context.preferences.system.ui_scale


def view_to_region(x: int, y: int):
    """Converts the given view coordinates to region coordinates"""
    for region in bpy.context.area.regions:
        if region.type == "WINDOW":
            return region.view2d.view_to_region(
                x * ui_scale(), y * ui_scale(), clip=False
            )
    return (x, y)


def get_node_top_left(node: bpy.types.Node) -> Tuple[float, float]:
    """Returns the top left coordinates of the given node"""
    x, y = view_to_region(node.location[0], node.location[1])
    return (x, y)


def get_zoom_level():
    """Returns the current zoom level of the node editor"""
    for region in bpy.context.area.regions:
        if region.type == "WINDOW":
            test_length = 1000
            x0, y0 = view_to_region(0, 0)
            x1, y1 = view_to_region(test_length, test_length)
            xl = x1 - x0
            yl = y1 - y0
            return math.sqrt(xl**2 + yl**2) / test_length * ui_scale()
    return 1 * ui_scale()


def draw_rect(x1, y1, x2, y2, shader):
    """Draws a rectangle"""
    indices = ((0, 1, 2), (2, 1, 3))

    vertices = ((x1, y1), (x2, y1), (x1, y2), (x2, y2))

    batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
    batch.draw(shader)


def draw_filled_circle(center, radius, segments, shader):
    """Draw a filled circle using the GPU module."""

    # Generate vertices for the circle
    vertices = [center]
    for i in range(segments):
        angle = 2.0 * 3.1415926 * float(i) / float(segments)
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        vertex = (center[0] + dx, center[1] + dy)
        vertices.append(vertex)
    vertices.append(vertices[1])  # Close the circle

    # Generate indices for triangle fan
    indices = [(0, i, i + 1) for i in range(1, segments + 1)]

    # Create batch and draw
    batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=indices)
    batch.draw(shader)


shader = gpu.shader.from_builtin("UNIFORM_COLOR")


def draw_error_marker(node: bpy.types.Node):
    """Draws an indicator on the screen edge showing nodes with errors"""
    size = 40
    offset = 30
    x, y = get_node_top_left(node)
    header = 0
    npanel = 0
    for region in bpy.context.area.regions:
        if region.type == "HEADER" and bpy.context.area.spaces[0].show_region_header:
            header = region.height
        if region.type == "UI":
            npanel = region.width
    x = max(min(x + offset, bpy.context.area.width - offset - npanel), offset)
    y = max(min(y + offset, bpy.context.area.height - offset - header), offset)
    # border
    shader.uniform_float("color", (0.35, 0, 0.05, 1))
    draw_filled_circle((x, y), size / 2, 16, shader)
    # circle
    shader.uniform_float("color", (1, 0.4, 0.6, 1))
    draw_filled_circle((x, y - 2), size / 2 - 2, 16, shader)
    # exclamation mark
    shader.uniform_float("color", (0.35, 0, 0.05, 1))
    draw_filled_circle((x, y - 10), 4, 8, shader)
    draw_rect(x - 3, y - 4, x + 3, y + 12, shader)


def draw_node_overlays():
    """Draws node details to the interface"""
    if not in_sn_tree(bpy.context):
        return
    zoom = get_zoom_level()
    font_id = get_monospace_font()
    blf.size(font_id, 8 * zoom)

    for node in bpy.context.space_data.node_tree.nodes:
        x, y = get_node_top_left(node)

        # if node.was_registered:
        # offset = 10 * zoom
        # shader.uniform_float("color", (0, 0.7, 0.25, 0.15))
        # draw_rect(
        #     x,
        #     y,
        #     x + (node.dimensions[0] * zoom),
        #     y - 200,
        #     shader,
        # )

        if hasattr(node, "id") and node.id in _node_times:
            padding_x = 5 * zoom
            padding_y = 4 * zoom
            margin_x = 8 * zoom

            error = get_node_error_msg(node)
            if error:
                # draw error marker
                draw_error_marker(node)

            # draw red overlay (and error text?)
            # offset = 10*zoom
            # shader.uniform_float("color", (.7, 0, .15, 0.15))
            # draw_rect(x-offset, y+offset, x+node.width, y-node.height, shader)

            # # draw timings
            # x_offset = x + margin_x
            # text = f"{round(_node_times[node.id], 1)} ms"
            # width, height = blf.dimensions(font_id, text)
            # line_width = 0.7*zoom

            # shader.uniform_float("color", (0.05, 0.05, 0.05, 0.3))
            # draw_rect(x_offset-line_width, y-line_width, x_offset+width+padding_x*2+line_width, y+height+padding_y*2+line_width, shader)
            # shader.uniform_float("color", (.15, .15, .15, .5))
            # draw_rect(x_offset, y, x_offset+width+padding_x*2, y+height+padding_y*2, shader)

            # blf.position(font_id, x_offset+padding_x, y+padding_y, 0)
            # blf.draw(font_id, text)
