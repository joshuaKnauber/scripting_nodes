import bpy

from ..base_socket import ScriptingBaseSocket


class ScriptingVectorSocket(ScriptingBaseSocket):
    bl_idname = "ScriptingVectorSocket"
    bl_label = "Vector"
    color = (0.380, 0.341, 0.839, 1)

    dimension: bpy.props.EnumProperty(
        name="Dimensions",
        items=[("2", "Vec2", ""), ("3", "Vec3", ""), ("4", "Vec4", "")],
        default="3",
        update=ScriptingBaseSocket.update_value,
    )
    value: bpy.props.FloatVectorProperty(
        size=4, default=(0.0, 0.0, 0.0, 0.0), update=ScriptingBaseSocket.update_value
    )

    def literal(self):
        values = [repr(float(v)) for v in self.value[: int(self.dimension)]]
        return f"({', '.join(values)})"

    def draw_value(self, context, layout, text):
        col = layout.column(align=True)
        if text:
            col.label(text=text)
        for i in range(int(self.dimension)):
            col.prop(self, "value", index=i, text="")
