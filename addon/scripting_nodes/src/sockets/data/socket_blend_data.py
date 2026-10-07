import bpy

from ...blend_data.rna import display_name
from ...lib.sockets import from_socket
from ..base_socket import ScriptingBaseSocket


class ScriptingBlendDataSocket(ScriptingBaseSocket):
    """Blender data (an Object, a Scene, a collection of Modifiers, ...).

    `blend_type` is the struct type of the value ("" = unknown) and
    `is_collection` marks a collection of that type. Both are set from the
    node's socket declaration (see blend_data/rna.blend_data_spec).
    """

    bl_idname = "ScriptingBlendDataSocket"
    bl_label = "Blend Data"
    color = (0.0, 0.75, 0.65, 1)

    blend_type: bpy.props.StringProperty()
    is_collection: bpy.props.BoolProperty()

    @property
    def socket_shape(self):
        return "SQUARE" if self.is_collection else "CIRCLE"

    def draw(self, context, layout, node, text):
        super().draw(context, layout, node, text)
        if not self.blend_type:
            return
        name = display_name(self.blend_type)
        # "Active Object" already says it's an Object, "Camera" doesn't
        if name.lower() not in text.lower():
            sub = layout.row()
            sub.active = False
            sub.label(text=name)


def linked_rna_type(socket):
    """(rna_type, is_collection) of what is connected to input `socket`;
    ("", False) when unknown or not Blender data."""
    if socket is None:
        return "", False
    source = from_socket(socket)
    if source is None or source.bl_idname != ScriptingBlendDataSocket.bl_idname:
        return "", False
    return source.blend_type, source.is_collection
