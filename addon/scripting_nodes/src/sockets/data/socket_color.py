import bpy

from ..base_socket import ScriptingBaseSocket


class ScriptingColorSocket(ScriptingBaseSocket):
    bl_idname = "ScriptingColorSocket"
    bl_label = "Color"
    color = (0.929, 0.851, 0.251, 1)

    use_alpha: bpy.props.BoolProperty(
        default=False, update=ScriptingBaseSocket.update_value
    )
    value: bpy.props.FloatVectorProperty(
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=ScriptingBaseSocket.update_value,
    )

    def literal(self):
        values = [repr(float(v)) for v in self.value[: 4 if self.use_alpha else 3]]
        return f"({', '.join(values)})"

    def draw_value(self, context, layout, text):
        layout.prop(self, "value", text=text)
