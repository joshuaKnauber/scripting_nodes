import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_input



class SN_UpdatePropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_UpdatePropertyNode"
    bl_label = "Update Property"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_outside_update(self, string_data):
        if self.copied_path:
            data = get_data(self.copied_path)
            new_data = get_data(string_data)
            if data and data["group_path"] in ["self", "context.preferences.addons[__name__.partition('.')[0]].preferences"]:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        if data["property"]["type"] != new_data["property"]["type"]:
                            self["copied_path"] = string_data
                            self.change_socket_type(self.outputs[1], self.prop_types[new_data["property"]["type"]])

                        self.outputs[1].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.outputs[1].variable_name = new_data["property"]["identifier"]
                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = "Update " + new_data["property"]["name"]
                    self.outputs[1].default_text = new_data["property"]["name"]
                    self["copied_path"] = string_data
            elif data:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        if data["property"]["type"] != new_data["property"]["type"]:
                            self["copied_path"] = string_data
                            self.change_socket_type(self.outputs[1], self.prop_types[new_data["property"]["type"]])

                        self.outputs[1].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.outputs[1].variable_name = new_data["property"]["identifier"]
                    inp = self.inputs[0]
                    if inp.default_text != new_data["data_block"]["name"]:
                        inp.default_text = new_data["data_block"]["name"]
                        inp.data_type = new_data["data_block"]["type"]
                        inp.data_name = new_data["data_block"]["name"]
                        self["copied_path"] = string_data

                    if new_data["property"]["removed"]:
                        self.copied_path = ""

                elif data["property"]["identifier"] == new_data["property"]["identifier"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    self.label = "Update " + new_data["property"]["name"]
                    self.outputs[1].default_text = new_data["property"]["name"]
                    self["copied_path"] = string_data


    def update_copied(self,context):
        if self.copied_path:
            data = get_data(self.copied_path)
            if data:
                self.label = "Update " + data["property"]["name"]
                if not data["data_block"]["type"] == "":
                    setup_data_input(self, data)
                    self.add_output_from_data(data["property"])
                else:
                    self.add_output_from_data(data["property"])
            else:
                self.copied_path = ""

        else:
            self.inputs.clear()
            self.remove_output_range(1)
            self.wrong_add = True
        self.auto_compile()

    copied_path: bpy.props.StringProperty(update=update_copied)
    wrong_add: bpy.props.BoolProperty(default=False)


    def on_create(self,context):
        self.add_execute_output("On Update")
        self.copied_path = self.copied_path

    def on_copy(self, node):
        self.copied_path = ""


    def draw_node(self, context, layout):
        if self.wrong_add:
            row = layout.row()
            row.alert = True
            row.label(text="You need to add this node using a getter")


    def code_imperative(self, context):

        if not self.copied_path:
            self.add_error("No property", "You need to add this node from a property")
            return {"code": ""}
        
        json = get_data(self.copied_path)
        data = json["property"]["identifier"]
        if json["property"]["created_from"] != "SN_CUSTOM":
            data += "_" + json["property"]["created_from"]

        code = self.outputs[0].code(6)
        return {
            "code": f"""
                    def update_{data}(self, context):
                        {code if code.strip() else "pass"}
                    """
        }


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