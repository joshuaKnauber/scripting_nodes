#SN_CastVectorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CastVectorNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CastVectorNode"
    bl_label = "Cast To Vector"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.6,0.2,0.8)
    should_be_registered = False

    use_four_numbers: bpy.props.BoolProperty(default=False,name="Use Four Numbers", description="Outputs a vector with four numbers instead of three")

    def inititialize(self, context):
        self.sockets.create_input(self,"DATA","Data")
        self.sockets.create_output(self,"INTEGER","Integer")

    def draw_buttons(self,context,layout):
        layout.prop(self,"use_four_numbers")

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}
