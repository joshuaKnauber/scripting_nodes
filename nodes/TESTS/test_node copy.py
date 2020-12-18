import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_OtherTestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OtherTestNode"
    bl_label = "Print Test"
    bl_icon = "GRAPH"
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
        "starts_tree": True
    }


    def on_create(self,context):
        self.add_string_input("inp")
        
        
    def code_evaluate(self, context, main_tree, touched_socket):
        return {
            "code": f"""
                    # {self.inputs[0].value}
                    
                    """
        }