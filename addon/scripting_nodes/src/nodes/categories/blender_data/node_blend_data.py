"""Blender Data node: follows one data path (`context.active_object.modifiers[...]`)
and outputs the value with its real type (nodes/_blend_path.py)."""

import bpy

from ....blend_data import rna
from ....core.context import NodeError
from ..._blend_path import BlendPathMixin
from ...base_node import ScriptingBaseNode


def _preset(label, root, path):
    return (label, {"path_root": root, "path": path})


class SNA_Node_BlendData(BlendPathMixin, ScriptingBaseNode, bpy.types.Node):
    """Blender data by path: the active object, a scene's frame rate, all
    materials of the file, a modifier of the connected object, ..."""

    bl_idname = "SNA_Node_BlendData"
    bl_label = "Blender Data"
    bl_width_default = 260

    # add menu entries that add this node set up (categories.py)
    sn_presets = [
        _preset("Active Object", "CONTEXT", "active_object"),
        _preset("Selected Objects", "CONTEXT", "selected_objects"),
        _preset("Scene", "CONTEXT", "scene"),
        _preset("View Layer", "CONTEXT", "view_layer"),
        _preset("Window Manager", "CONTEXT", "window_manager"),
        _preset("Preferences", "CONTEXT", "preferences"),
        _preset("Blend File", "DATA", ""),
        _preset("All Objects", "DATA", "objects"),
    ]
    sn_menu_operators = [("sna.paste_blender_path", "Paste Data Path", "PASTEDOWN")]

    def socket_specs(self):
        final = self.path_final()
        label = rna.label(final) if self.path or self.path_root != "INPUT" else "Value"
        return self.path_input_specs(), [rna.value_spec(final, "value", label)]

    def draw_label(self):
        return self.path_label() or self.bl_label

    def draw(self, context, layout):
        self.draw_path(layout)

    def emit(self, ctx):
        if not self.path and self.path_root != "DATA":
            raise NodeError("Search or paste a data path")
        ctx.output("value", self.path_expression(ctx))
