from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingIntegerSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingIntegerSocket"
    bl_label = "Integer"

    def update_value(self, context):
        self.node._generate()

    value: bpy.props.IntProperty(default=1, update=update_value)

    def _to_code(self):
        return f"{self.value}"

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=self.name)

    @classmethod
    def draw_color_simple(cls):
        return (0.32, 0.65, 0.35, 1)
