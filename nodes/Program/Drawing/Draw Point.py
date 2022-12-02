import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_DrawPointNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DrawPointNode"
    bl_label = "Draw Point"
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

        self.add_float_input("Size").default_value = 1

        self.add_enum_input("On Top")["items"] = str(["NONE", "ALWAYS", "LESS", "LESS_EQUAL", "EQUAL", "GREATER", "GREATER_EQUAL"])

        inp = self.add_float_vector_input("Location")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        self.add_execute_output()
        self.ref_ntree = self.node_tree

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        
    def evaluate(self, context):
        self.code_import = f"""
            import gpu
            from gpu_extras.batch import batch_for_shader
        """

        coords = f"coords = ("
        for inp in self.inputs:
            if inp.name == "Location" and not inp.dynamic:
                coords += f"{inp.python_value}, "
        coords += ")"

        self.code = f"""
            {coords}

            shader = gpu.shader.from_builtin('{"3" if self.use_3d else "2"}D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'POINTS', {{"pos": coords}})

            shader.bind()
            shader.uniform_float("color", {self.inputs["Color"].python_value})

            gpu.state.point_size_set({self.inputs["Size"].python_value})

            gpu.state.depth_test_set({self.inputs["On Top"].python_value})
            gpu.state.depth_mask_set(True)

            batch.draw(shader)
            {self.indent(self.outputs[0].python_value, 3)}
        """