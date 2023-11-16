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

    use_3d: bpy.props.BoolProperty(
        name="Use 3D",
        description="Whether to use 3D or 2D coordinates",
        default=False,
        update=update_use3d,
    )

    def update_use_loc_list(self, context):
        self.inputs["Line Locations"].set_hide(not self.use_loc_list)
        for inp in self.inputs:
            if inp.bl_label == "Float Vector" and inp.subtype == "NONE":
                inp.set_hide(self.use_loc_list)
        self._evaluate(context)

    use_loc_list: bpy.props.BoolProperty(
        name="Draw Multiple",
        description="Whether to draw multiple points (this is more efficient than separate nodes)",
        default=False,
        update=update_use_loc_list,
    )

    def on_create(self, context):
        self.add_execute_input()

        inp = self.add_float_vector_input("Color")
        inp.subtype = "COLOR_ALPHA"

        self.add_float_input("Width").default_value = 1

        self.add_enum_input("On Top")["items"] = str(
            [
                "NONE",
                "ALWAYS",
                "LESS",
                "LESS_EQUAL",
                "EQUAL",
                "GREATER",
                "GREATER_EQUAL",
            ]
        )

        inp = self.add_float_vector_input("Point 1")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 0
        inp.default_value[2] = 0

        inp = self.add_float_vector_input("Point 2")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 1
        inp.default_value[2] = 1

        inp = self.add_list_input("Line Locations")
        inp.set_hide(True)

        self.add_execute_output()

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        layout.prop(self, "use_loc_list", text="Draw Multiple")

    def evaluate(self, context):
        self.code_import = f"""
            import gpu
            import gpu_extras
        """

        p1 = self.inputs["Point 1"].python_value
        p2 = self.inputs["Point 2"].python_value

        lines = f"""
            lines = [({p1}, {p2})]
        """

        if self.use_loc_list:
            lines = f"lines = {self.inputs['Line Locations'].python_value}"

        coords = f"""
            {lines}
            coords = []
            indices = []
            for i, line in enumerate(lines):
                coords.extend(line)
                indices.append((i*2, i*2+1))
        """

        self.code = f"""
            {coords}

            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = gpu_extras.batch.batch_for_shader(shader, 'LINES', {{"pos": coords}}, indices=tuple(indices))

            shader.bind()
            shader.uniform_float("color", {self.inputs["Color"].python_value})

            gpu.state.line_width_set({self.inputs["Width"].python_value})

            {f"gpu.state.depth_test_set({self.inputs['On Top'].python_value})" if self.use_3d else ""}
            {"gpu.state.depth_mask_set(True)" if self.use_3d else ""}

            gpu.state.blend_set('ALPHA')
            batch.draw(shader)
            {self.indent(self.outputs[0].python_value, 3)}
        """
