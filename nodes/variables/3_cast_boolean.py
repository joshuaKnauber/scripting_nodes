#SN_CastBooleanNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CastBooleanNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CastBooleanNode"
    bl_label = "Cast To Boolean"
    bl_icon = "DRIVER_TRANSFORM"
    bl_width_default = 130
    node_color = (0.65,0,0)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self,"DATA","Data")
        self.sockets.create_output(self,"BOOLEAN","Boolean")

    def evaluate(self, socket, node_data, errors):
        blocks = [{"lines": [["bool(", node_data["input_data"][0]["code"], ")"]],"indented": []}]
        return {"blocks": blocks, "errors": errors}

