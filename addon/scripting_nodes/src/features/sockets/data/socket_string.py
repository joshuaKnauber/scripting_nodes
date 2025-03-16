from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingStringSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingStringSocket"
    bl_label = "String"

    def update_value(self, context):
        self.node._generate()

    value: bpy.props.StringProperty(
        default="", update=update_value, options={"TEXTEDIT_UPDATE"}
    )

    is_dynamic: bpy.props.BoolProperty(
        name="Dynamic", description="Allow removing inputs", default=False
    )

    def _to_code(self):
        return f'"{self.value}"'

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            if self.is_dynamic:
                row = layout.row(align=False)
                row.prop(self, "value", text="")
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
        return (0.4, 0.6, 1, 1)
