import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from ..Properties.property_util import get_data, setup_data_socket



class SN_DisplayPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayPropertyNode"
    bl_label = "Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    

    def on_create(self,context):
        self.add_interface_input("Property").mirror_name = True
        self.add_string_input("Text")
        self.add_boolean_input("Emboss")
        
        
    def setup_inputs(self,prop_type):
        if prop_type == "BOOLEAN":
            self.add_boolean_input("Toggle").set_default(False)
            self.add_boolean_input("Invert Checkbox").set_default(False)
        elif prop_type == "ENUM":
            self.add_boolean_input("Expand").set_default(False)
        elif prop_type in ["FLOAT","INT"]:
            self.add_boolean_input("Slider").set_default(False)
        self.add_icon_input("Icon")
            

    def update_copied(self,context):
        labels = {
            "STRING": "Text Input",
            "BOOLEAN": "Checkbox",
            "FLOAT": "Number Input",
            "INT": "Number Input",
            "ENUM": "Dropdown"
        }
        
        if self.copied_path:
            data = get_data(self.copied_path)
            if data:
                self.label = labels[data["type"]]
                self.setup_inputs(data["type"])
                self.inputs["Text"].set_default(data["name"])
                self.prop_name = data["name"]
                setup_data_socket(self, data)
                
        else:
            self.label = "Property"
            self.prop_name = ""
            self.inputs["Text"].set_default("")
            for i in range(len(self.inputs)-1,2,-1):
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
        
        if not self.copied_path: return {"code": ""}

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)
        
        values = ""
        for inp in self.inputs:
            if not inp.socket_type in ["BLEND_DATA","ICON","INTERFACE"]:
                values += inp.name.lower().replace("_"," ") + "=" + inp.code() + ","
            
        data = get_data(self.copied_path)

        if self.inputs[-1].socket_type == "BLEND_DATA":
            data_path = self.inputs[-1].code() + data["full_path"].split("]")[-1]
        else:
            data_path = "self"
        
        return {
            "code": f"""
                    {layout}.prop({data_path},"{data["identifier"]}",icon_value={self.inputs['Icon'].code()},{values})
                    """
        }