import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_ObjectsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectsNode"
    bl_label = "Objects"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_blend_data_output("All Objects")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""

                    """
        }