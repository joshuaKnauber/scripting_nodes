import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_BreakNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BreakNode"
    bl_label = "Break loop early"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_execute_input("Break")


    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"""
                    break
                    """
        }