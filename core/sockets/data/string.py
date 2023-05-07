import bpy
from ..base_socket import ScriptingSocket
from ....utils.codify import codify_string_value


class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_StringSocket"

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    value: bpy.props.StringProperty(
        default="", update=lambda self, _: self.node._update())

    @property
    def value_code(self):
        return codify_string_value(self.value)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            layout.prop(self, "value", text=text)
        else:
            layout.label(text=text)
