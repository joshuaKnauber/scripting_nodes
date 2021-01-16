import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_input



class SN_SetAttributeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetAttributeNode"
    bl_label = "Set Attribute"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_blend_data_input("Blend Data").mirror_name = True
        self.add_string_input("Attribute")
        self.add_data_input("Data")
        self.add_execute_output("Execute")
    

    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"""
                    setattr({self.inputs[1].code()},{self.inputs[2].code()},{self.inputs[3].code()})
                    {self.outputs[0].code(5)}
                    """
        }