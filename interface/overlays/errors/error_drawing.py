import os

import blf
import bpy

from ....utils.is_serpens import in_sn_tree
from ..nodes.node_overlays import get_monospace_font, get_node_error_msg


def draw_errors():
    """ Draws the errors to the interface """
    global _errors
    if not in_sn_tree(bpy.context):
        return
    font_id = get_monospace_font()
    blf.size(font_id, 20)
    blf.enable(font_id, blf.WORD_WRAP)
    blf.word_wrap(font_id, 800)
    top = 40
    left = 40
    i = 0
    for node in bpy.context.space_data.node_tree.nodes:
        if getattr(node, "is_sn", False):
            error = get_node_error_msg(node)
            if error:
                blf.color(font_id, 1, 1, 1, 1 - i*0.2)
                blf.position(font_id, left, bpy.context.region.height - top, 0)
                blf.draw(font_id, error)
                _, height = blf.dimensions(font_id, error)
                top += height + 20
                i += 1
    if i == 0:
        blf.color(font_id, 1, 1, 1, 1)
        blf.position(font_id, left, bpy.context.region.height - top, 0)
        blf.draw(font_id, "No errors")
    blf.disable(font_id, blf.WORD_WRAP)
