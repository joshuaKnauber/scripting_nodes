import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_GetBlendDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetBlendDataNode"
    bl_label = "Get Blend Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").copy_name = True
        
        
    def update_outputs(self):
        pass
        
        
    def on_link_insert(link):
        if link.to_socket == self.inputs[0]:
            self.update_outputs()


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""

                    """
        }