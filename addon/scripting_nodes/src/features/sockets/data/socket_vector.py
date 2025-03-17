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

    is_dynamic: bpy.props.BoolProperty(
        name="Dynamic", description="Allow removing inputs", default=False
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

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)

            if self.is_dynamic:
                row = layout.row(align=False)
                row.scale_x = 0.9

                for icon, operator_name in [
                    ("TRIA_UP", "sna.insert_socket"),
                    ("REMOVE", "sna.remove_socket"),
                ]:
                    op = row.operator(operator_name, text="", icon=icon, emboss=False)
                    op.node_name = node.name
                    op.tree_name = node.id_data.name

                    if operator_name == "sna.insert_socket":
                        op.socket_type = self.bl_idname
                        op.socket_name = self.name

                    for i, s in enumerate(node.inputs):
                        if s == self:
                            op.socket_index = i
                            break

        else:
            dim = int(self.dimension)
            col = layout.column(align=True)
            for i in range(dim):
                col.prop(self, "value", index=i, text="")

            if self.is_dynamic:
                layout.separator(factor=0.5)
                row = layout.row(align=True)
                row.scale_x = 0.9

                for icon, operator_name in [
                    ("TRIA_UP", "sna.insert_socket"),
                    ("REMOVE", "sna.remove_socket"),
                ]:
                    op = row.operator(operator_name, text="", icon=icon, emboss=False)
                    op.node_name = node.name
                    op.tree_name = node.id_data.name

                    if operator_name == "sna.insert_socket":
                        op.socket_type = self.bl_idname
                        op.socket_name = self.name

                    for i, s in enumerate(node.inputs):
                        if s == self:
                            op.socket_index = i
                            break

    @classmethod
    def draw_color_simple(cls):
        return (0.380, 0.341, 0.839, 1)
