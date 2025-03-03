from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingVectorSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingVectorSocket"
    bl_label = "Vector"

    def update_value(self, context):
        self.node._generate()

    def update_dimensions(self, context):
        self.node._generate()

    # Vector dimension options
    dimension_items = [
        ("2", "Vec2", "Two-dimensional vector"),
        ("3", "Vec3", "Three-dimensional vector"),
        ("4", "Vec4", "Four-dimensional vector (with w component)"),
    ]

    dimension: bpy.props.EnumProperty(
        name="Dimensions",
        description="Vector dimensions",
        items=dimension_items,
        default="3",
        update=update_dimensions,
    )

    # Define vector properties
    value_x: bpy.props.FloatProperty(default=0.0, update=update_value)
    value_y: bpy.props.FloatProperty(default=0.0, update=update_value)
    value_z: bpy.props.FloatProperty(default=0.0, update=update_value)
    value_w: bpy.props.FloatProperty(default=0.0, update=update_value)

    def _to_code(self):
        if self.dimension == "2":
            return f"({self.value_x}, {self.value_y})"
        elif self.dimension == "3":
            return f"({self.value_x}, {self.value_y}, {self.value_z})"
        else:  # dimension == '4'
            return f"({self.value_x}, {self.value_y}, {self.value_z}, {self.value_w})"

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            column = layout.column(align=True)

            # Header with dimension selector
            row = column.row()
            row.label(text=self.name)
            row.prop(self, "dimension", text="")

            # Vector components based on dimension
            column.prop(self, "value_x", text="X")
            column.prop(self, "value_y", text="Y")

            if self.dimension in ("3", "4"):
                column.prop(self, "value_z", text="Z")

            if self.dimension == "4":
                column.prop(self, "value_w", text="W")

    @classmethod
    def draw_color_simple(cls):
        return (0.380, 0.341, 0.839, 1)
