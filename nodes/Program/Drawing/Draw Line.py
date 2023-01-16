import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_DrawLineNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_DrawLineNode"
    bl_label = "Draw Line"
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

        self.add_float_input("Width").default_value = 1

        self.add_enum_input("On Top")["items"] = str(["NONE", "ALWAYS", "LESS", "LESS_EQUAL", "EQUAL", "GREATER", "GREATER_EQUAL"])

        inp = self.add_float_vector_input("Point 1")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        inp = self.add_float_vector_input("Point 2")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 0
        inp.default_value[2] = 1

        self.add_execute_output()
        self.ref_ntree = self.node_tree

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        
    def evaluate(self, context):
        self.code_import = f"""
            import gpu
            from gpu_extras.batch import batch_for_shader
        """

        p1 = self.inputs["Point 1"].python_value
        p2 = self.inputs["Point 2"].python_value

        coords = f"""
            coords = (({p1}[0], {p1}[1]), ({p2}[0], {p2}[1]))
        """
        if self.use_3d:
            coords = f"""
            coords = (({p1}[0], {p1}[1], {p1}[2]), ({p2}[0], {p2}[1], {p2}[2]))
            """

        self.code = f"""
            {coords}

            shader = gpu.shader.from_builtin('{"3" if self.use_3d else "2"}D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {{"pos": coords}})

            shader.bind()
            shader.uniform_float("color", {self.inputs["Color"].python_value})

            gpu.state.line_width_set({self.inputs["Width"].python_value})

            gpu.state.depth_test_set({self.inputs["On Top"].python_value})
            gpu.state.depth_mask_set(True)

            batch.draw(shader)
            {self.indent(self.outputs[0].python_value, 3)}
        """