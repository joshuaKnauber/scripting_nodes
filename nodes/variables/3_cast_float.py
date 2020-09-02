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

    def evaluate(self, socket, node_data, errors):
        block = []
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname in ["SN_BoolSocket", "SN_FloatSocket", "SN_IntSocket"]:
                blocks = [{"lines": [["float(", node_data["input_data"][0]["code"], ")"]],"indented": []}]
            elif self.inputs[0].links[0].from_socket.bl_idname in ["SN_VectorSocket", "SN_StringSocket"]:
                blocks = [{"lines": [["cast_float(", node_data["input_data"][0]["code"], ")"]],"indented": []}]

        return {"blocks": blocks, "errors": errors}
