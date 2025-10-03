from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingListSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingListSocket"
    bl_label = "List"
    socket_shape = "SQUARE"

    def update_value(self, context):
        self.node._generate()

    value: bpy.props.StringProperty(
        default="[]", update=update_value, options={"TEXTEDIT_UPDATE"}
    )

    def _to_code(self):
        return f"{self.value}"

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)

    @classmethod
    def draw_color_simple(cls):
        return (0.85, 0.14, 1.0, 1)
