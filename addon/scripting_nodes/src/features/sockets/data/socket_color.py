from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingColorSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingColorSocket"
    bl_label = "Color"

    use_alpha: bpy.props.BoolProperty(default=False)

    def _to_code(self):
        if self.use_alpha:
            return (
                f"({self.value[0]}, {self.value[1]}, {self.value[2]}, {self.value[3]})"
            )
        else:
            return f"({self.value[0]}, {self.value[1]}, {self.value[2]})"

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.label(text=text)

    @classmethod
    def draw_color_simple(cls):
        return (0.929, 0.851, 0.251, 1)
