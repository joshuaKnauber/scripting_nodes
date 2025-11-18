import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_DrawQuadNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DrawQuadNode"
    bl_label = "Draw Quad"
    node_color = "PROGRAM"

    def update_use3d(self, context):
        for input in self.inputs:
            if input.bl_label == "Float Vector" and input.subtype == "NONE":
                input.size = 3 if self.use_3d else 2
        self.inputs["On Top"].set_hide(not self.use_3d)
        self.inputs["Backface Culling"].set_hide(not self.use_3d)
        self._evaluate(context)

    use_3d: bpy.props.BoolProperty(
        name="Use 3D",
        description="Whether to use 3D or 2D coordinates",
        default=False,
        update=update_use3d,
    )

    def update_use_loc_list(self, context):
        self.inputs["Quad Locations"].set_hide(not self.use_loc_list)
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

        self.add_enum_input("On Top").items = str(
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

        self.add_boolean_input("Backface Culling").default_value = True

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

        inp = self.add_list_input("Quad Locations")
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

        bl = self.inputs["Bottom Left"].python_value
        br = self.inputs["Bottom Right"].python_value
        tl = self.inputs["Top Left"].python_value
        tr = self.inputs["Top Right"].python_value

        quad_locations = (
            f"quads = [[tuple({bl}), tuple({br}), tuple({tl}), tuple({tr})]]"
        )

        if self.use_loc_list:
            quad_locations = f"quads = {self.inputs['Quad Locations'].python_value}"

        verts = f"""
            {quad_locations}
            vertices = []
            indices = []
            for i_{self.static_uid}, quad in enumerate(quads):
                vertices.extend(quad)
                indices.extend([(i_{self.static_uid} * 4, i_{self.static_uid} * 4 + 1, i_{self.static_uid} * 4 + 2), (i_{self.static_uid} * 4 + 2, i_{self.static_uid} * 4 + 1, i_{self.static_uid} * 4 + 3)])
        """

        self.code = f"""
            {verts}

            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = gpu_extras.batch.batch_for_shader(shader, 'TRIS', {{"pos": tuple(vertices)}}, indices=tuple(indices))

            shader.bind()
            shader.uniform_float("color", {self.inputs["Color"].python_value})

            {f"gpu.state.depth_test_set({self.inputs['On Top'].python_value})" if self.use_3d else ""}
            {"gpu.state.depth_mask_set(True)" if self.use_3d else ""}

            {f"gpu.state.face_culling_set('BACK' if {self.inputs['Backface Culling'].python_value} else 'NONE')" if self.use_3d else ""}

            gpu.state.blend_set('ALPHA')
            batch.draw(shader)
            {self.indent(self.outputs[0].python_value, 3)}
        """
