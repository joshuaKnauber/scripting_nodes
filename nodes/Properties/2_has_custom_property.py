import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_input



class SN_HasCustomPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_HasCustomPropertyNode"
    bl_label = "Has Custom Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def on_create(self,context):
        self.add_blend_data_input("Blend Data").mirror_name = True
        self.add_string_input("Custom Property")
        self.add_boolean_output("Has Custom Property")
    

    def code_evaluate(self, context, touched_socket):
        if not self.inputs[1].links:
            self.add_error("No blend data", "Blend data input is not connected", True)
            return {"code": "False"}

        return {
            "code": f"{self.inputs[1].code()} in {self.inputs[0].code()}"
        }