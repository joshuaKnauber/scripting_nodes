import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_BooleanVectorNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_BooleanVectorNode"
    bl_label = "Boolean Vector"
    node_color = "VECTOR"

    def on_create(self, context):
        self.add_boolean_vector_input("Boolean").set_hide(True)
        self.add_boolean_vector_output("Boolean")

    def evaluate(self, context):
        self.outputs["Boolean"].python_value = self.inputs["Boolean"].python_value

    def draw_node(self, context, layout):
        layout.prop(self.inputs["Boolean"], "size")
        self.inputs["Boolean"].draw_socket(context, layout, self, "Value")