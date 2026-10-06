from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingColorSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingColorSocket"
    bl_label = "Color"

    def update_value(self, context):
        self.node._generate()

    use_alpha: bpy.props.BoolProperty(default=False)

    value: bpy.props.FloatVectorProperty(
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_value,
    )

    def _to_code(self):
        if self.use_alpha:
            return (
                f"({self.value[0]}, {self.value[1]}, {self.value[2]}, {self.value[3]})"
            )
        else:
            return f"({self.value[0]}, {self.value[1]}, {self.value[2]})"

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            row = layout.row()
            row.prop(self, "value", text=text)

    @classmethod
    def draw_color_simple(cls):
        return (0.929, 0.851, 0.251, 1)
