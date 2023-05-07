import bpy
from ..base_socket import ScriptingSocket


class SN_BooleanSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_BooleanSocket"

    def get_color(self, context, node):
        return (0.95, 0.73, 1)

    value: bpy.props.BoolProperty(
        default=False, update=lambda self, _: self.node._update())

    @property
    def value_code(self):
        return str(self.value)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            layout.prop(self, "value", text=text)
        else:
            layout.label(text=text)
