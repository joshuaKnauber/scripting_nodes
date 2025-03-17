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

    is_dynamic: bpy.props.BoolProperty(
        name="Dynamic", description="Allow removing inputs", default=False
    )

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
            layout.prop(self, "value", text=self.name)

        if self.is_dynamic:
            row = layout.row()
            buttons = row.row(align=True)
            buttons.scale_x = 0.9

            for icon, operator_name in [
                ("TRIA_UP", "sna.insert_socket"),
                ("REMOVE", "sna.remove_socket"),
            ]:
                op = buttons.operator(operator_name, text="", icon=icon, emboss=False)
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
        return (0.929, 0.851, 0.251, 1)
