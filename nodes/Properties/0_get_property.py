import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_socket



class SN_GetPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetPropertyNode"
    bl_label = "Get Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    

    def update_copied(self,context):
        if self.copied_path:
            data = get_data(self.copied_path)
            if data:
                self.label = "Get " + data["name"]
                self.prop_name = data["name"]
                setup_data_socket(self, data)
                self.add_output_from_type(data["data_block"]["type"],data["identifier"])
                
        else:
            self.label = "Get Property"
            self.prop_name = ""
            self.inputs.clear()
            self.outputs.clear()
    
    
    copied_path: bpy.props.StringProperty(update=update_copied)
    prop_name: bpy.props.StringProperty()
        

    def draw_node(self,context,layout):
        if not self.copied_path:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_property_path",text="Paste Property",icon="PASTEDOWN").node = self.name
        else:
            layout.operator("sn.reset_property_node",icon="UNLINKED",text=self.prop_name).node = self.name
    

    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"{self.inputs[0].code()}.{self.outputs[0].variable_name}"
        }