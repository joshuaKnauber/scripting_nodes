import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from ..Properties.property_util import setup_sockets



class SN_DisplayPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayPropertyNode"
    bl_label = "Property"
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

    def on_create(self,context):
        self.add_interface_input("Property").copy_name = True
        
    def setup_inputs(self,prop_type,prop_name):
        if prop_type == "BOOLEAN":
            self.add_string_input("Text").set_default(prop_name)
            self.add_boolean_input("Toggle").set_default(False)
            self.add_boolean_input("Emboss")
            self.add_boolean_input("Invert Checkbox").set_default(False)
            self.add_icon_input("Icon")
        elif prop_type == "STRING":
            self.add_string_input("Text").set_default(prop_name)
            self.add_boolean_input("Emboss")
            self.add_icon_input("Icon")
        elif prop_type == "ENUM":
            self.add_string_input("Text").set_default(prop_name)
            self.add_boolean_input("Expand").set_default(False)
            self.add_boolean_input("Emboss")
            self.add_icon_input("Icon")
        elif prop_type in ["FLOAT","INT"]:
            self.add_string_input("Text").set_default(prop_name)
            self.add_boolean_input("Slider").set_default(False)
            self.add_boolean_input("Emboss")
            self.add_icon_input("Icon")
            

    def get_copied(self,context):
        if self.copied_path:
            path_details = self.get_details()
            if path_details:
                self.label = "Property (" + path_details["prop_name"] + ")"
                self.setup_inputs(path_details["prop_type"], path_details["prop_name"])
                setup_sockets(self, path_details)
        else:
            for i in range(len(self.inputs)-1,-1,-1):
                if i:
                    self.inputs.remove(self.inputs[i])
    
    
    copied_path: bpy.props.StringProperty(update=get_copied)
        

    def draw_node(self,context,layout):
        if not self.copied_path:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_property_path",text="Paste Property",icon="PASTEDOWN").node = self.name
        else:
            layout.operator("sn.reset_node",icon="UNLINKED").node = self.name
                    

    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)

        icon = self.inputs['Icon'].icon_line()
        
        values = ""
        for inp in self.inputs:
            if inp.name == "Text":
                values += f"text={inp.value},"
            elif inp.name == "Toggle":
                values += f"toggle={inp.value},"
            elif inp.name == "Emboss":
                values += f"emboss={inp.value},"
            elif inp.name == "Invert Checkbox":
                values += f"invert_checkbox={inp.value},"
            elif inp.name == "Expand":
                values += f"expand={inp.value},"
            elif inp.name == "Slider":
                values += f"slider={inp.value},"
        
        return {
            "code": f"""
                    {layout}.prop({self.inputs[-1].value},"{self.get_details()["prop_identifier"]}",{icon}{values})
                    """
        }