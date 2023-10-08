import bpy

from ..base_socket import ScriptingSocket


class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_BooleanSocket"

    value: bpy.props.BoolProperty(default=False, update=lambda self, _: self.node.mark_dirty())

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "False"
        return str(self.value)

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.95, 0.73, 1, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output:
            layout.prop(self, "value", text="" if self.is_output else text)
        else:
            layout.label(text=text)
