from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingDynamicAddInputSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingDynamicAddInputSocket"
    bl_label = "Dynamic Add Input"

    add_socket_type: bpy.props.StringProperty(default="ScriptingDataSocket")
    add_socket_name: bpy.props.StringProperty(default="Item")

    def draw(self, context, layout, node, text):
        row = layout.row()
        op = row.operator("sna.add_socket", text=text, icon="ADD", emboss=False)
        op.node_name = node.name
        op.tree_name = node.id_data.name
        op.socket_type = self.add_socket_type
        op.socket_name = self.add_socket_name

    def _to_code(self):
        return ""

    @classmethod
    def draw_color_simple(cls):
        return (0.0, 0.0, 0.0, 0.0)
