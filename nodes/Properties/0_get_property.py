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


    def on_outside_update(self, string_data):
        if self.copied_path:
            print(self.copied_path)
            data = get_data(self.copied_path)
            new_data = get_data(string_data)
            if data and data["group_path"] in ["self", f"context.preferences.addons['{bpy.context.scene.sn.addon_tree().sn_graphs[0].short()}'].preferences"]:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        if data["property"]["type"] != new_data["property"]["type"]:
                            self["copied_path"] = string_data
                            self.change_socket_type(self.outputs[0], self.prop_types[new_data["property"]["type"]])

                        self.outputs[0].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.outputs[0].variable_name = new_data["property"]["identifier"]
                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = "Get " + new_data["property"]["name"]
                    self.prop_name = new_data["property"]["name"]
                    self.outputs[0].default_text = new_data["property"]["name"]
                    self["copied_path"] = string_data
            elif data:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        if data["property"]["type"] != new_data["property"]["type"]:
                            self["copied_path"] = string_data
                            self.change_socket_type(self.outputs[0], self.prop_types[new_data["property"]["type"]])

                        self.outputs[0].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.outputs[0].variable_name = new_data["property"]["identifier"]
                    inp = self.inputs[0]
                    if inp.default_text != new_data["data_block"]["name"]:
                        inp.default_text = new_data["data_block"]["name"]
                        inp.data_type = new_data["data_block"]["type"]
                        inp.data_name = new_data["data_block"]["name"]
                        self["copied_path"] = string_data

                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = "Get " + new_data["property"]["name"]
                    self.prop_name = new_data["property"]["name"]
                    self.outputs[0].default_text = new_data["property"]["name"]
                    self["copied_path"] = string_data


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

        data = get_data(self.copied_path)
        path = ""
        if len(self.inputs):
            if not self.inputs[0].links:
                self.add_error("No blend data", "Blend data input is not connected", True)
                return {"code": "None"}

            path = self.inputs[0].code()

        if data["group_path"]:
            path += "." + data["group_path"] if path else data["group_path"]

        if not '["' in data["property"]["identifier"]:
            path += "."
        path += data["property"]["identifier"]

        return {
            "code": f"{path}"
        }