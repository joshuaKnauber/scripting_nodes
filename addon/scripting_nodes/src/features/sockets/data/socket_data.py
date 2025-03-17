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
        row = layout.row()

        if self.is_dynamic:
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
        return (0.35, 0.35, 0.35, 1)
