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
            if self.is_dynamic:
                row = layout.row(align=False)
                row.prop(self, "value", text=self.name)
                op = row.operator("sna.remove_socket", text="", icon="X", emboss=False)
                op.node_name = node.name
                op.tree_name = node.id_data.name
                for i, s in enumerate(node.inputs):
                    if s == self:
                        op.socket_index = i
                        break
            else:
                layout.prop(self, "value", text=self.name)

    @classmethod
    def draw_color_simple(cls):
        return (0.929, 0.851, 0.251, 1)
