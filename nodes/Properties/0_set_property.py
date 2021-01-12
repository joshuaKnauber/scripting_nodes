import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_socket



class SN_SetPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetPropertyNode"
    bl_label = "Set Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def on_create(self,context):
        self.add_execute_input("Set Property")
        self.add_execute_output("Execute")
    

    def update_copied(self,context):
        if self.copied_path:
            data = get_data(self.copied_path)
            if data:
                self.label = "Set " + data["name"]
                self.prop_name = data["name"]
                if not data["full_path"] == "self":
                    setup_data_socket(self, data)
                    self.add_input_from_type(data["data_block"]["type"],data["identifier"])
                else:
                    self.add_input_from_data(data["data_block"])
                
        else:
            self.label = "Set Property"
            self.prop_name = ""
            for i in range(len(self.inputs)-1,0,-1):
                self.inputs.remove(self.inputs[i])
    
    
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
        
        if len(self.inputs) > 1:
            if not get_data(self.copied_path)["full_path"] == "self":
                return {
                    "code": f"""
                            {self.inputs[1].code()}.{self.inputs[2].variable_name} = {self.inputs[2].code()}
                            {self.outputs[0].code(7)}
                            """
                }
            else:
                return {
                    "code": f"""
                            self.{self.inputs[1].variable_name} = {self.inputs[1].code()}
                            {self.outputs[0].code(7)}
                            """
                }
            
        else:
            return {"code":f"""
                            {self.outputs[0].code(7)}
                            """}