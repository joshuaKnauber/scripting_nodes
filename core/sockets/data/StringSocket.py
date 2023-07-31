import bpy

from ..base_socket import ScriptingSocket


class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_StringSocket"

    value: bpy.props.StringProperty(default="", update=lambda self, _: self.node.compile())

    def value_code(self):
        value = self.value.replace('\'', '\\\'')
        return f"'{value}'"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.44, 0.7, 1, 1)

    def draw_socket(self, context, layout, node, text, draw_linked_value, draw_output_value):
        if (not self.is_output or draw_output_value) and (not self.is_linked or draw_linked_value):
            layout.prop(self, "value", text="" if self.is_output else text)
        else:
            layout.label(text=text)
