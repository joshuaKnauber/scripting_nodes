import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from ..Properties.property_util import get_data, setup_data_input



class SN_DisplayPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayPropertyNode"
    bl_label = "Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_outside_update(self, string_data):
        if self.copied_path:
            labels = {"STRING": "Text Input","BOOLEAN": "Checkbox","FLOAT": "Number Input","INTEGER": "Number Input","INT": "Number Input","ENUM": "Dropdown", "POINTER": "Pointer", "COLLECTION": "Collection"}
            data = get_data(self.copied_path)
            new_data = get_data(string_data)
            if data and data["group_path"] in ["self", f"context.preferences.addons['{bpy.context.scene.sn.addon_tree().sn_graphs[0].short()}'].preferences"]:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        self.label = labels[new_data["property"]["type"]]
                        if new_data["property"]["type"] != data["property"]["type"]:
                            for i in range(len(self.inputs)-1,2,-1):
                                self.inputs.remove(self.inputs[i])
                            self.setup_inputs(new_data["property"]["type"])
                        self["copied_path"] = string_data
                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = labels[data["property"]["type"]]
                    self.prop_name = new_data["property"]["name"]
                    self["copied_path"] = string_data

            else:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        self.label = labels[new_data["property"]["type"]]
                        if new_data["property"]["type"] != data["property"]["type"]:
                            for i in range(len(self.inputs)-1,2,-1):
                                self.inputs.remove(self.inputs[i])
                            self.setup_inputs(new_data["property"]["type"])
                            setup_data_input(self, new_data)
                        self["copied_path"] = string_data
                    inp = self.inputs[-1]
                    if inp.default_text != new_data["data_block"]["name"]:
                        inp.default_text = new_data["data_block"]["name"]
                        inp.data_type = new_data["data_block"]["type"]
                        inp.data_name = new_data["data_block"]["name"]
                        self["copied_path"] = string_data
                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = labels[data["property"]["type"]]
                    self.prop_name = new_data["property"]["name"]
                    self["copied_path"] = string_data


    def on_create(self,context):
        self.add_interface_input("Interface").mirror_name = True
        self.add_string_input("Text")
        self.add_boolean_input("Emboss")
        
        
    def setup_inputs(self,prop_type):
        if prop_type == "BOOLEAN":
            self.add_boolean_input("Toggle").set_default(False)
            self.add_boolean_input("Invert Checkbox").set_default(False)
            self.add_icon_input("Icon")
        elif prop_type == "ENUM":
            self.add_boolean_input("Expand").set_default(False)
            self.add_icon_input("Icon")
        elif prop_type in ["FLOAT","INT", "INTEGER"]:
            self.add_boolean_input("Slider").set_default(False)
        else:
            self.add_icon_input("Icon")
            

    def update_copied(self,context):
        labels = {
            "STRING": "Text Input",
            "BOOLEAN": "Checkbox",
            "FLOAT": "Number Input",
            "INT": "Number Input",
            "INTEGER": "Number Input",
            "ENUM": "Dropdown",
            "POINTER": "Pointer",
            "COLLECTION": "Collection"
        }

        if self.copied_path:
            data = get_data(self.copied_path)
            if data:
                self.label = labels[data["property"]["type"]]
                self.setup_inputs(data["property"]["type"])
                self.prop_type = data["property"]["type"]
                self.inputs["Text"].set_default(data["property"]["name"])
                self.prop_name = data["property"]["name"]
                if data["data_block"]["type"]:
                    setup_data_input(self, data)

            else:
                self.copied_path = ""
                
        else:
            self.label = "Property"
            self.prop_name = ""
            self.inputs["Text"].set_default("")
            for i in range(len(self.inputs)-1,2,-1):
                self.inputs.remove(self.inputs[i])
    
    
    copied_path: bpy.props.StringProperty(update=update_copied)
    prop_name: bpy.props.StringProperty()
    prop_type: bpy.props.StringProperty()


    def update_color_wheel(self,context):
        for inp in self.inputs:
            if not inp.socket_type in ["INTERFACE","BLEND_DATA"]:
                inp.hide = self.color_wheel


    color_wheel: bpy.props.BoolProperty(default=False,name="Show Color Wheel",description="Show this property as a color wheel (only for color properties)",update=update_color_wheel)
    cw_value_slider: bpy.props.BoolProperty(default=False,name="Show Value Slider",description="Show a value slider for the color wheel")


    def draw_node(self,context,layout):
        if not self.copied_path:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_property_path",text="Paste Property",icon="PASTEDOWN").node = self.name
        else:
            layout.operator("sn.reset_property_node",icon="UNLINKED",text=self.prop_name).node = self.name

            if self.prop_type == "FLOAT":
                layout.prop(self,"color_wheel")
                if self.color_wheel:
                    layout.prop(self,"cw_value_slider")


    def code_evaluate(self, context, touched_socket):

        if not self.copied_path:
            self.add_error("No property copied", "There is no property copied", True)
            return {"code": ""}

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)

        values = ""
        for inp in self.inputs:
            if not inp.socket_type in ["BLEND_DATA","ICON","INTERFACE"]:
                values += inp.name.lower().replace(" ","_") + "=" + inp.code() + ","

        data = get_data(self.copied_path)

        data_path = ""
        if self.inputs[-1].socket_type == "BLEND_DATA":
            data_path = self.inputs[-1].code()
            if not self.inputs[-1].links:
                self.add_error("No blend data", "Blend data input is not connected", True)
                return {"code": ""}

        if data["group_path"]:
            data_path += "." + data["group_path"] if data_path else data["group_path"]
            
        icon = ""
        if "Icon" in self.inputs:
            icon = f",icon_value={self.inputs['Icon'].code()}"
        
        if not self.color_wheel:
            return {"code": f"""
                    {layout}.prop({data_path},'{data["property"]["identifier"]}'{icon},{values})
                    """}
        else:
            return {"code": f"""
                    {layout}.template_color_picker({data_path},"{data["property"]["identifier"]}",value_slider={self.cw_value_slider})
                    """}