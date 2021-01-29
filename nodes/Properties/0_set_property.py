import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_input



class SN_SetPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetPropertyNode"
    bl_label = "Set Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_outside_update(self, string_data):
        if self.copied_path:
            data = get_data(self.copied_path)
            new_data = get_data(string_data)
            if data and data["group_path"] == "self":
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        if data["property"]["type"] != new_data["property"]["type"]:
                            self["copied_path"] = string_data
                            self.change_socket_type(self.inputs[1], self.prop_types[new_data["property"]["type"]])

                        if data["property"]["subtype"] != new_data["property"]["subtype"]:
                            self["copied_path"] = string_data

                        self.inputs[1].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.inputs[1].variable_name = new_data["property"]["identifier"]
                    if new_data["property"]["type"] == "ENUM":
                        self.inputs[1].enum_values = new_data["property"]["items"]
                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = "Set " + new_data["property"]["name"]
                    self.prop_name = new_data["property"]["name"]
                    self.inputs[1].default_text = new_data["property"]["name"]
                    self["copied_path"] = string_data

            elif data:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        if data["property"]["type"] != new_data["property"]["type"]:
                            self["copied_path"] = string_data
                            self.change_socket_type(self.inputs[2], self.prop_types[new_data["property"]["type"]])

                        if data["property"]["subtype"] != new_data["property"]["subtype"]:
                            self["copied_path"] = string_data

                        self.inputs[2].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.inputs[2].variable_name = new_data["property"]["identifier"]
                    if new_data["property"]["type"] == "ENUM":
                        self.inputs[2].enum_values = new_data["property"]["items"]
                    inp = self.inputs[1]
                    if inp.default_text != new_data["data_block"]["name"]:
                        inp.default_text = new_data["data_block"]["name"]
                        inp.data_type = new_data["data_block"]["type"]
                        inp.data_name = new_data["data_block"]["name"]
                        self["copied_path"] = string_data

                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = "Set " + new_data["property"]["name"]
                    self.prop_name = new_data["property"]["name"]
                    self.inputs[2].default_text = new_data["property"]["name"]
                    self["copied_path"] = string_data

    
    def on_create(self,context):
        self.add_execute_input("Set Property")
        self.add_execute_output("Execute").mirror_name = True
    

    def update_copied(self,context):
        if self.copied_path:
            data = get_data(self.copied_path)
            if data:
                self.label = "Set " + data["property"]["name"]
                self.prop_name = data["property"]["name"]
                if not data["data_block"]["type"] == "":
                    setup_data_input(self, data)
                    self.add_input_from_data(data["property"])
                else:
                    self.add_input_from_data(data["property"])
            else:
                self.copied_path = ""
                
        else:
            self.label = "Set Property"
            self.prop_name = ""
            for i in range(len(self.inputs)-1,0,-1):
                self.inputs.remove(self.inputs[i])
        self.auto_compile()
    
    
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
        
        set_prop = ""
        data = get_data(self.copied_path)

        if len(self.inputs) > 1:
            if len(self.inputs) == 3:
                set_prop = self.inputs[1].code()
        
            if data["group_path"]:
                set_prop += "." + data["group_path"] if set_prop else data["group_path"]
                
            set_prop += "." + data["property"]["identifier"]
            
            set_prop += " = " + self.inputs[-1].code()

            if self.inputs[1].socket_type == "BLEND_DATA":
                if not self.inputs[1].links:
                    self.add_error("No blend data", "Blend data input is not connected", True)
                    return {
                        "code": f"""
                                {self.outputs[0].code(8)}
                                """
                    }
        else:
            self.add_error("No Property", "You need to paste the property you want to set", True)
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }

        return {
            "code": f"""
                    {set_prop}
                    {self.outputs[0].code(5)}
                    """
        }