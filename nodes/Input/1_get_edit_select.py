import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_GetEditSelectNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetEditSelectNode"
    bl_label = "Get Edit Select Mode"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_boolean_output("Vertex")
        self.add_boolean_output("Edge")
        self.add_boolean_output("Face")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"bpy.context.tool_settings.mesh_select_mode[{self.outputs.find(touched_socket.name)}]"
        }