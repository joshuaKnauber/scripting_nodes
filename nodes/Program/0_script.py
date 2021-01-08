import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ScriptNode"
    bl_label = "Script"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True
    }


    def on_create(self,context):
        self.add_execute_output("Script")


    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"""
                    {self.outputs[0].code(5)}
                    """
        }