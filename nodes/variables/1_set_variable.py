#SN_SetVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SetVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_SetVariableNode"
    bl_label = "Set Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.75,0.75,70.75)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self,"STRING","String")
        self.sockets.create_output(self,"BOOLEAN","Boolean")

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}
