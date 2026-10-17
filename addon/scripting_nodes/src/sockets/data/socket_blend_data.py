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
    bl_label = "Blender Data"
    color = (0.0, 0.75, 0.65, 1)

    blend_type: bpy.props.StringProperty()
    is_collection: bpy.props.BoolProperty()

    @property
    def socket_shape(self):
        return "SQUARE" if self.is_collection else "CIRCLE"

    def draw(self, context, layout, node, text):
        name = display_name(self.blend_type) if self.blend_type else ""
        # "Active Object" already says it's an Object, "Camera" doesn't
        if not name or name.lower() in text.lower():
            super().draw(context, layout, node, text)
        elif self.is_output or self.is_linked:
            custom = getattr(node, "draw_socket", None)
            if custom is None or not custom(context, self, layout, text):
                draw_type_row(layout, text, name, node.width, right=self.is_output)
        else:
            super().draw(context, layout, node, text)


def _text_width(text):
    import blf

    blf.size(0, 11)  # the node font at zoom 1, relative to node.width
    return blf.dimensions(0, text)[0]


def draw_type_row(layout, text, type_label, node_width, right=False, picker=None):
    """ "Camera  Object": a socket label with its type, dimmed (no type if
    it's ""). `picker(row)` adds a button to change the type."""
    if right:
        # socket rows ignore alignment: push the row right with a spacer
        needed = _text_width(text) + 12
        if type_label:
            needed += _text_width(type_label) + 8
        if picker is not None:
            needed += 22
        factor = 1 - needed / max(node_width - 20, 1)
        if factor > 0.02:
            split = layout.split(factor=factor)
            split.label(text="")
            layout = split
    row = layout.row(align=True)
    row.label(text=text)
    sub = row.row(align=True)
    sub.active = False
    if type_label:
        sub.label(text=type_label)
    if picker is not None:
        picker(sub)


def linked_rna_type(socket):
    """(rna_type, is_collection) of what is connected to input `socket`;
    ("", False) when unknown or not Blender data."""
    if socket is None:
        return "", False
    source = from_socket(socket)
    if source is None or source.bl_idname != ScriptingBlendDataSocket.bl_idname:
        return "", False
    return source.blend_type, source.is_collection
