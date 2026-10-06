from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingFloatSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingFloatSocket"
    bl_label = "Float"

    def update_value(self, context):
        self.node._generate()

    value: bpy.props.FloatProperty(default=1, update=update_value)

    def _to_code(self):
        return f"{self.value}"

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=self.name)

    @classmethod
    def draw_color_simple(cls):
        return (0.65, 0.65, 0.65, 1)
