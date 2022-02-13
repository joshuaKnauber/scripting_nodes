import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_CombineStringsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CombineStringsNode"
    bl_label = "Combine Strings"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("String")
        self.add_string_input("String")
        self.add_dynamic_string_input("String")
        self.add_string_output("Combined String")

    def evaluate(self, context):
        values = [" + " + inp.python_value for inp in self.inputs[1:-1]]
        self.outputs["Combined String"].python_value = self.inputs[0].python_value + "".join(values)