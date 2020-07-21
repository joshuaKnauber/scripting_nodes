#SN_CastIntegerNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CastIntegerNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CastIntegerNode"
    bl_label = "Cast To Integer"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.2,0.4,0.75)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self,"DATA","Data")
        self.sockets.create_output(self,"INTEGER","Integer")

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}
