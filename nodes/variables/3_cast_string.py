#SN_CastStringNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CastStringNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CastStringNode"
    bl_label = "Cast To String"
    bl_icon = "DRIVER_TRANSFORM"
    bl_width_default = 130
    node_color = (0,0.75,0)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self,"DATA","Data")
        self.sockets.create_output(self,"STRING","String")

    def evaluate(self, socket, input_data, errors):
        blocks = [{"lines": [["str(", input_data[0]["code"], ")"]],"indented": []}]
        return {"blocks": blocks, "errors": errors}
