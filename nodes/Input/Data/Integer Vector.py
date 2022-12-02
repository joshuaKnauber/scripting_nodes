import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_IntegerVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IntegerVectorNode"
    bl_label = "Integer Vector"
    node_color = "VECTOR"

    def on_create(self, context):
        self.add_integer_vector_input("Integer").set_hide(True)
        self.add_integer_vector_output("Integer")

    def evaluate(self, context):
        self.outputs["Integer"].python_value = self.inputs["Integer"].python_value

    def draw_node(self, context, layout):
        layout.prop(self.inputs["Integer"], "size")
        self.inputs["Integer"].draw_socket(context, layout, self, "Value")