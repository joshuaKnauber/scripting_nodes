#SN_CastFloatNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CastFloatNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CastFloatNode"
    bl_label = "Cast To Float"
    bl_icon = "DRIVER_TRANSFORM"
    bl_width_default = 130
    node_color = (0.23,0.65,0.75)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self,"DATA","Data")
        self.sockets.create_output(self,"FLOAT","Float")

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}
