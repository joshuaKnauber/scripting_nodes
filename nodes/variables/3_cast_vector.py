#SN_CastVectorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CastVectorNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CastVectorNode"
    bl_label = "Cast To Vector"
    bl_icon = "DRIVER_TRANSFORM"
    bl_width_default = 130
    node_color = (0.6,0.2,0.8)
    should_be_registered = False

    def update_inputs(self, context):
        if self.use_four_numbers:
            self.sockets.create_input(self, "FLOAT", "Fourth Number")
        else:
            self.inputs.remove(self.inputs[1])

    use_four_numbers: bpy.props.BoolProperty(default=False,name="Use Four Numbers", description="Outputs a vector with four numbers instead of three", update=update_inputs)

    def inititialize(self, context):
        self.sockets.create_input(self,"DATA","Data")
        self.sockets.create_output(self,"VECTOR","Vector")

    def draw_buttons(self,context,layout):
        layout.prop(self,"use_four_numbers")

    def evaluate(self, socket, input_data, errors):
        if self.use_four_numbers:
            blocks = [{"lines": [["cast_four_vector(", input_data[0]["code"], ", " + input_data[1]["code"] + ")"]],"indented": []}]
        else:
            blocks = [{"lines": [["cast_vector(", input_data[0]["code"], ")"]],"indented": []}]
        return {"blocks": blocks, "errors": errors}
