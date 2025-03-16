from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingDataSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingDataSocket"
    bl_label = "Data"

    is_dynamic: bpy.props.BoolProperty(
        name="Dynamic", description="Allow removing inputs", default=False
    )

    def _to_code(self):
        return "None"

    def draw(self, context, layout, node, text):
        layout.label(text=text)
        if self.is_dynamic:
            row = layout.row(align=False)
            op = row.operator("sna.remove_socket", text="", icon="X", emboss=False)
            op.node_name = node.name
            op.tree_name = node.id_data.name
            for i, s in enumerate(node.inputs):
                if s == self:
                    op.socket_index = i
                    break

    @classmethod
    def draw_color_simple(cls):
        return (0.35, 0.35, 0.35, 1)
