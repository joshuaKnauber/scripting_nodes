import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_FloatVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FloatVectorNode"
    bl_label = "Float Vector"
    node_color = "VECTOR"

    def on_create(self, context):
        self.add_float_vector_input("Float").set_hide(True)
        self.add_float_vector_output("Float")

    def evaluate(self, context):
        self.outputs["Float"].python_value = self.inputs["Float"].python_value

    def draw_node(self, context, layout):
        layout.prop(self.inputs["Float"], "size")
        self.inputs["Float"].draw_socket(context, layout, self, "Value")