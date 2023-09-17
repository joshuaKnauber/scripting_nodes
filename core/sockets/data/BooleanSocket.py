import bpy

from ..base_socket import ScriptingSocket


class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_BooleanSocket"

    value: bpy.props.BoolProperty(default=False, update=lambda self, _: self.node.mark_dirty())

    def value_code(self):
        return str(self.value)

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.95, 0.73, 1, 1)

    def draw_socket(self, context, layout, node, text, draw_linked_value, draw_output_value):
        if (not self.is_output or draw_output_value) and (not self.is_linked or draw_linked_value):
            layout.prop(self, "value", text="" if self.is_output else text)
        else:
            layout.label(text=text)
