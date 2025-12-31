import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_DrawCircleNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_DrawCircleNode"
    bl_label = "Draw Circle"
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
        self.add_execute_input()

        inp = self.add_float_vector_input("Color")
        inp.subtype = "COLOR_ALPHA"

        self.add_float_input("Radius").default_value = 1
        self.add_float_input("Width").default_value = 1
        self.add_integer_input("Segments").default_value = 32

        self.add_enum_input("On Top").items = str(["NONE", "ALWAYS", "LESS", "LESS_EQUAL", "EQUAL", "GREATER", "GREATER_EQUAL"])

        inp = self.add_float_vector_input("Location")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        self.add_execute_output()

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        
    def evaluate(self, context):
        self.code_import = f"""
            import gpu
            import gpu_extras.presets as gpu_extras_presets
        """

        self.code = f"""
            gpu.state.line_width_set({self.inputs["Width"].python_value})
            gpu.state.depth_test_set({self.inputs["On Top"].python_value})
            gpu.state.depth_mask_set(True)
            gpu.state.blend_set('ALPHA')

            gpu_extras_presets.draw_circle_2d({self.inputs["Location"].python_value}, {self.inputs["Color"].python_value}, {self.inputs["Radius"].python_value}, segments={self.inputs["Segments"].python_value})

            {self.indent(self.outputs[0].python_value, 3)}
        """