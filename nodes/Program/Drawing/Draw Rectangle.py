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
        self._evaluate(context)

    use_3d: bpy.props.BoolProperty(name="Use 3D",
                                description="Whether to use 3D or 2D coordinates",
                                default=False,
                                update=update_use3d)

    def on_create(self, context):
        self.add_execute_input()

        inp = self.add_float_vector_input("Color")
        inp.subtype = "COLOR_ALPHA"

        self.add_enum_input("On Top")["items"] = str(["NONE", "ALWAYS", "LESS", "LESS_EQUAL", "EQUAL", "GREATER", "GREATER_EQUAL"])

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

        inp = self.add_float_vector_input("Top Left")
        inp.size = 2
        inp.default_value[0] = 0
        inp.default_value[1] = 1
        inp.default_value[2] = 1

        inp = self.add_float_vector_input("Top Right")
        inp.size = 2
        inp.default_value[0] = 1
        inp.default_value[1] = 1
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

        bl = self.inputs["Bottom Left"].python_value
        br = self.inputs["Bottom Right"].python_value
        tl = self.inputs["Top Left"].python_value
        tr = self.inputs["Top Right"].python_value

        verts = f"""
            vertices = (
                ({bl}[0], {bl}[1]), ({br}[0], {br}[1]),
                ({tl}[0], {tl}[1]), ({tr}[0], {tr}[1]))
        """
        if self.use_3d:
            verts = f"""
            vertices = (
                ({bl}[0], {bl}[1], {bl}[2]), ({br}[0], {br}[1], {br}[2]),
                ({tl}[0], {tl}[1], {tl}[2]), ({tr}[0], {tr}[1], {tr}[2]))
            """

        self.code = f"""
            {verts}

            indices = ((0, 1, 2), (2, 1, 3))

            shader = gpu.shader.from_builtin('{"3" if self.use_3d else "2"}D_UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {{"pos": vertices}}, indices=indices)

            shader.bind()
            shader.uniform_float("color", {self.inputs["Color"].python_value})

            gpu.state.depth_test_set({self.inputs["On Top"].python_value})
            gpu.state.depth_mask_set(True)

            gpu.state.face_culling_set("BACK" if {self.inputs["Backface Culling"].python_value} else "NONE")

            gpu.state.blend_set('ALPHA')
            batch.draw(shader)
            {self.indent(self.outputs[0].python_value, 3)}
        """