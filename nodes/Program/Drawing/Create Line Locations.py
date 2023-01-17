import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CreateLineLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_CreateLineLocationsNode"
    bl_label = "Create Line"
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

        self.add_list_output("Line")

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d", text="Use 3D")
        
    def evaluate(self, context):
        p1 = self.inputs["Point 1"].python_value
        p2 = self.inputs["Point 2"].python_value

        self.outputs[0].python_value = f"[{p1}, {p2}]"