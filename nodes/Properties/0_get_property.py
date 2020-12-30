import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from .property_util import setup_sockets


class SN_GetPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetPropertyNode"
    bl_label = "Get Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
        
    def get_details(self):
        try:
            path_details = json.loads(self.copied_path)
            return path_details
        except:
            return None
                         
                
    def get_copied(self,context):
        if self.copied_path:
            path_details = self.get_details()
            if path_details:
                setup_sockets(self, path_details)
                out = self.add_output_from_type(path_details["prop_type"],path_details["prop_name"],path_details["prop_array_length"])
                # out.is_expression = True
                # out.editable_var_name = False
                # out.var_name = path_details["prop_name"]

    
    
    copied_path: bpy.props.StringProperty(update=get_copied)
    
    
    def reset_node(self):
        self.copied_path = ""
        self.inputs.clear()
        self.outputs.clear()
        

    def draw_node(self,context,layout):
        if not self.copied_path:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_property_path",text="Paste Property",icon="PASTEDOWN").node = self.name
    

    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"{self.inputs[0].value}.{self.get_details()['prop_identifier']}"
        }