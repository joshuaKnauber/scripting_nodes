from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_Vector(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Vector"
    bl_label = "Vector"

    def update_dimensions(self, context):
        self.outputs[0].dimension = self.dimension
        self._generate()

    dimension: bpy.props.EnumProperty(
        name="Dimensions",
        description="Vector dimensions",
        items=[
            ("2", "Vec2", "Two-dimensional vector"),
            ("3", "Vec3", "Three-dimensional vector"),
            ("4", "Vec4", "Four-dimensional vector (with w component)"),
        ],
        default="3",
        update=update_dimensions,
    )

    vector: bpy.props.FloatVectorProperty(
        name="Vector",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        update=lambda self, context: self._generate(),
    )

    def draw(self, context, layout):
        layout.prop(self, "dimension", text="")
        col = layout.column(align=True)
        col.prop(self, "vector", index=0, text="")
        col.prop(self, "vector", index=1, text="")

        if self.dimension in ("3", "4"):
            col.prop(self, "vector", index=2, text="")

        if self.dimension == "4":
            col.prop(self, "vector", index=3, text="")

    def on_create(self):
        self.add_output("ScriptingVectorSocket")
        self.outputs[0].dimension = self.dimension

    def generate(self):
        if self.dimension == "2":
            self.outputs[0].code = f"({self.vector[0]}, {self.vector[1]})"
        elif self.dimension == "3":
            self.outputs[0].code = (
                f"({self.vector[0]}, {self.vector[1]}, {self.vector[2]})"
            )
        else:
            self.outputs[0].code = (
                f"({self.vector[0]}, {self.vector[1]}, {self.vector[2]}, {self.vector[3]})"
            )
