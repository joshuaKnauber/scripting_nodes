import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CreateQuadLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_CreateQuadLocationsNode"
    bl_label = "Create Quad"
    node_color = "PROGRAM"

    def update_use3d(self, context):
        for input in self.inputs:
            if input.bl_label == "Float Vector" and input.subtype == "NONE":
                input.size = 3 if self.use_3d else 2
        self._evaluate(context)

    use_3d: bpy.props.BoolProperty(name="Use 3D",
                                description="Whether to use 3D or 2D coordinates",
                                default=False,
                                update=update_use3d)

    def on_create(self, context):
        inp = self.add_float_vector_input("Bottom Left")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        inp = self.add_float_vector_input("Bottom Right")
        inp.size = 2
        inp.default_value[0] = 1
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        inp = self.add_float_vector_input("Top Right")
        inp.size = 2
        inp.default_value[0] = 1
        inp.default_value[1] = 1
        inp.default_value[2] = 1

        inp = self.add_float_vector_input("Top Left")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 1
        inp.default_value[2] = 1

        self.add_list_output("Quad")

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        
    def evaluate(self, context):
        bl = self.inputs["Bottom Left"].python_value
        br = self.inputs["Bottom Right"].python_value
        tl = self.inputs["Top Left"].python_value
        tr = self.inputs["Top Right"].python_value

        self.outputs[0].python_value = f"[{bl}, {br}, {tl}, {tr}]"