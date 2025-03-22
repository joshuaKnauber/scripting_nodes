from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingVectorSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingVectorSocket"
    bl_label = "Vector"

    def update_value(self, context):
        self.node._generate()

    dimension: bpy.props.EnumProperty(
        name="Dimensions",
        description="Vector dimensions",
        items=[
            ("2", "Vec2", "Two-dimensional vector"),
            ("3", "Vec3", "Three-dimensional vector"),
            ("4", "Vec4", "Four-dimensional vector (with w component)"),
        ],
        default="3",
        update=update_value,
    )

    value: bpy.props.FloatVectorProperty(
        name="Value",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        subtype="NONE",
        update=update_value,
    )

    def _to_code(self):
        if self.dimension == "2":
            return f"({self.value[0]}, {self.value[1]})"
        elif self.dimension == "3":
            return f"({self.value[0]}, {self.value[1]}, {self.value[2]})"
        else:
            return (
                f"({self.value[0]}, {self.value[1]}, {self.value[2]}, {self.value[3]})"
            )

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            col = layout.column(align=True)
            dim = int(self.dimension)
            col.prop(self, "value", index=0, text="")
            col.prop(self, "value", index=1, text="")
            if dim >= 3:
                col.prop(self, "value", index=2, text="")
            if dim >= 4:
                col.prop(self, "value", index=3, text="")

    @classmethod
    def draw_color_simple(cls):
        return (0.380, 0.341, 0.839, 1)
