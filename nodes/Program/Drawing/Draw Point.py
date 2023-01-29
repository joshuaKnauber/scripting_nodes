import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_DrawPointNode(SN_ScriptingBaseNode, bpy.types.Node):

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

    def update_use_loc_list(self, context):
        if self.use_loc_list:
            self.convert_socket(self.inputs["Location"], self.socket_names["List"])
        else:
            self.convert_socket(self.inputs["Location"], self.socket_names["Float Vector"])
        self._evaluate(context)


    use_loc_list: bpy.props.BoolProperty(name="Draw Multiple",
                                description="Whether to draw multiple points (this is more efficient than separate nodes)",
                                default=False,
                                update=update_use_loc_list)

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

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        layout.prop(self, "use_loc_list", text="Draw Multiple")
        
    def evaluate(self, context):
        self.code_import = f"""
            import gpu
            import gpu_extras
        """

        coords = f"coords = ()"
        loc_inp = self.inputs["Location"]
        if loc_inp.bl_label == "Float Vector":
            coords = f"coords = ({loc_inp.python_value}, )"
        else:
            coords = f"coords = tuple({loc_inp.python_value})"

        self.code = f"""
            {coords}

            shader = gpu.shader.from_builtin('{"3" if self.use_3d else "2"}D_UNIFORM_COLOR')
            batch = gpu_extras.batch.batch_for_shader(shader, 'POINTS', {{"pos": coords}})

            shader.bind()
            shader.uniform_float("color", {self.inputs["Color"].python_value})

            gpu.state.point_size_set({self.inputs["Size"].python_value})

            gpu.state.depth_test_set({self.inputs["On Top"].python_value})
            gpu.state.depth_mask_set(True)

            gpu.state.blend_set('ALPHA')
            batch.draw(shader)
            {self.indent(self.outputs[0].python_value, 3)}
        """