#SN_GetCustomPropertiesNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_GetCustomPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetCustomPropertiesNode"
    bl_label = "Get Custom Properties"
    bl_icon = "MESH_CUBE"
    node_color = (0.2, 0.2, 0.2)
    bl_width_default = 180
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>get custom properties</>.",
                "",
                "Object Input: The object whos properties you want to get"],
        "python": ["bpy.data.objects[0]['prop']"]

    }

    def inititialize(self, context):
        self.sockets.create_input(self,"OBJECT","Data block")
        self.sockets.create_input(self,"STRING","Name")
        self.sockets.create_output(self,"FLOAT","Value")

    def evaluate(self, socket, node_data, errors):
        if node_data["input_data"][0]["code"]:
            return {"blocks": [{"lines": [[node_data["input_data"][0]["code"], "[", node_data["input_data"][1]["code"], "]"]],"indented": []}],"errors": errors}
        else:
            errors.append({"title": "No object data", "message": "You need to connect the object socket", "node": self, "fatal": True})
            return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

