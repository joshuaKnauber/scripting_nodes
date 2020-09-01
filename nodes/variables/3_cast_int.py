#SN_CastIntegerNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CastIntegerNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CastIntegerNode"
    bl_label = "Cast To Integer"
    bl_icon = "DRIVER_TRANSFORM"
    bl_width_default = 130
    node_color = (0.2,0.4,0.75)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self,"DATA","Data")
        self.sockets.create_output(self,"INTEGER","Integer")

    def evaluate(self, socket, node_data, errors):
        block = []
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname in ["SN_BoolSocket", "SN_FloatSocket", "SN_IntSocket"]:
                blocks = [{"lines": [["int(", node_data["input_data"][0]["code"], ")"]],"indented": []}]
            elif self.inputs[0].links[0].from_socket.bl_idname in ["SN_VectorSocket", "SN_StringSocket"]:
                blocks = [{"lines": [["cast_int(", node_data["input_data"][0]["code"], ")"]],"indented": []}]

        return {"blocks": blocks, "errors": errors}

