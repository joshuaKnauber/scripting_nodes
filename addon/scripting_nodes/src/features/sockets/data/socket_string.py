from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingStringSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingStringSocket"
    bl_label = "String"

    def update_value(self, context):
        self.node._generate()

    value: bpy.props.StringProperty(
        default="", update=update_value, options={"TEXTEDIT_UPDATE"}
    )

    def _to_code(self):
        return f'"{self.value}"'

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=self.name)

    @classmethod
    def draw_color_simple(cls):
        return (0.4, 0.6, 1, 1)
