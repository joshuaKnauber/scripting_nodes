#SN_SetCustomPropertiesNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SetCustomPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetCustomPropertiesNode"
    bl_label = "Set Custom Properties"
    bl_icon = "MESH_CUBE"
    node_color = (0.2, 0.2, 0.2)
    bl_width_default = 180
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>set custom properties</>.",
                "",
                "Object Input: The object whos properties you want to edit"],
        "python": ["bpy.data.objects[0]['prop'] = <string>\"Suzanne\"</>"]

    }

    def inititialize(self, context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"OBJECT","Data block")
        self.sockets.create_input(self,"STRING","Name")
        self.sockets.create_input(self,"FLOAT","Value")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        if node_data["input_data"][1]["code"]:
            return {"blocks": [{"lines": [[node_data["input_data"][1]["code"], "[", node_data["input_data"][2]["code"], "] = ", node_data["input_data"][3]["code"]]],"indented": []}, {"lines": [[next_code]],"indented": []}],"errors": errors}
        else:
            errors.append({"title": "No object data", "message": "You need to connect the object socket", "node": self, "fatal": True})
            return {"blocks": [{"lines": [[next_code]],"indented": []}],"errors": errors}

