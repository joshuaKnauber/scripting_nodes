import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CreateTriangleLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_CreateTriangleLocationsNode"
    bl_label = "Create Triangle"
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
        inp = self.add_float_vector_input("Corner 1")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        inp = self.add_float_vector_input("Corner 2")
        inp.size = 2
        inp.default_value[0] = 1
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        inp = self.add_float_vector_input("Corner 3")
        inp.size = 2
        inp.default_value[0] = 1
        inp.default_value[1] = 1
        inp.default_value[2] = 1

        self.add_list_output("Triangle")

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        
    def evaluate(self, context):
        c1 = self.inputs["Corner 1"].python_value
        c2 = self.inputs["Corner 2"].python_value
        c3 = self.inputs["Corner 3"].python_value

        self.outputs[0].python_value = f"[{c1}, {c2}, {c3}]"