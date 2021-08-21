import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode
from .property_util import get_data, setup_data_input, setup_data_output



class SN_UpdatePropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_UpdatePropertyNode"
    bl_label = "On Property Update"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_outside_update(self, string_data):
        if self.copied_path:
            data = get_data(self.copied_path)
            new_data = get_data(string_data)
            if data and data["group_path"] in ["self", f"context.preferences.addons['{bpy.context.scene.sn.addon_tree().sn_graphs[0].short()}'].preferences"]:
                if data["property"]["name"] == new_data["property"]["name"] and data["property"]["created_from"] == new_data["property"]["created_from"]:
                    if data["property"]["identifier"] != new_data["property"]["identifier"]:
                        self["copied_path"] = string_data
                    else:
                        if data["property"]["type"] != new_data["property"]["type"]:
                            self["copied_path"] = string_data
                            self.change_socket_type(self.outputs[1], self.prop_types[new_data["property"]["type"]])

                        if data["property"]["subtype"] != new_data["property"]["subtype"]:
                            self["copied_path"] = string_data

                        self.outputs[1].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.outputs[1].variable_name = new_data["property"]["identifier"]
                    if new_data["property"]["type"] == "ENUM":
                        if data["property"]["items"] != new_data["property"]["items"]:
                            self["copied_path"] = string_data
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

                        if data["property"]["subtype"] != new_data["property"]["subtype"]:
                            self["copied_path"] = string_data

                        self.outputs[1].subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])
                        self.outputs[1].variable_name = new_data["property"]["identifier"]
                    out = self.outputs[2]
                    if out.default_text != new_data["data_block"]["name"]:
                        out.default_text = new_data["data_block"]["name"]
                        out.data_type = new_data["data_block"]["type"]
                        out.data_name = new_data["data_block"]["name"]
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
                self.add_output_from_data(data["property"])
                self.label = "Update " + data["property"]["name"]
                if "context.preferences.addons" in data["group_path"]:
                    setup_data_output(self, {'data_block': {'name': 'Preferences', 'type': 'Preferences'}})
                elif data["group_path"] == "self":
                    setup_data_output(self, {'data_block': {'name': 'Operator', 'type': 'Operator'}})
                else:
                    setup_data_output(self, data)
            else:
                self.copied_path = ""

        else:
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

        if touched_socket == self.outputs[1]:
            data = get_data(self.copied_path)
            return {
                "code": f"self.{data['property']['identifier']}"
            }
        else:
            return {
                "code": f"self"
            }
