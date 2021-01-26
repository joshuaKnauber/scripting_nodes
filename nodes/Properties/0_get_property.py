import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_input



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
                self.label = "Get " + data["property"]["name"]
                self.prop_name = data["property"]["name"]
                if not data["data_block"]["type"] == "":
                    setup_data_input(self, data)
                    self.add_output_from_data(data["property"])
                else:
                    self.add_output_from_data(data["property"])
            else:
                self.copied_path = ""
                
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

        data = get_data(self.copied_path)
        path = ""
        if len(self.inputs):
            if not self.inputs[0].links:
                self.add_error("No blend data", "Blend data input is not connected", True)
                return {"code": "None"}

            path = self.inputs[0].code()

        if data["group_path"]:
            path += "." + data["group_path"] if path else data["group_path"]

        path += "." + data["property"]["identifier"]

        return {
            "code": f"{path}"
        }