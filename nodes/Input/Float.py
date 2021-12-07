import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_FloatNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FloatNode"
    bl_label = "Float"
    node_color = "FLOAT"

    def on_create(self, context):
        self.add_float_input("Float").hide = True
        self.add_float_output("Float")

    def evaluate(self, context):
        self.outputs["Float"].python_value = self.inputs["Float"].python_value

    def draw_node(self, context, layout):
        layout.prop(self.inputs["Float"], "default_value", text="")