import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_IntegerNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_IntegerNode"
    bl_label = "Integer"
    node_color = "INTEGER"

    def on_create(self, context):
        self.add_integer_input("Integer").set_hide(True)
        self.add_integer_output("Integer")

    def evaluate(self, context):
        self.outputs["Integer"].python_value = self.inputs["Integer"].python_value

    def draw_node(self, context, layout):
        layout.prop(self.inputs["Integer"], "default_value", text="")