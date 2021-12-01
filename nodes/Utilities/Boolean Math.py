import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BooleanMathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BooleanMathNode"
    bl_label = "Boolean Math"
    node_color = "BOOLEAN"

    def on_create(self, context):
        enum = self.add_enum_input("")
        enum.items = str(["and", "or"])
        self.add_boolean_input("Boolean")
        self.add_boolean_input("Boolean")
        self.add_dynamic_boolean_input("Boolean")
        self.add_boolean_output("Boolean")

    def evaluate(self, context):
        values = [inp.python_value for inp in self.inputs[1:-1]]
        join_op = f" {self.inputs[0].python_value} ".join(values)
        self.outputs["Boolean"].python_value = join_op