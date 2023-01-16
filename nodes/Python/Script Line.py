import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ScriptlineNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ScriptlineNode"
    bl_label = "Scriptline"
    node_color = "PROGRAM"
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_string_input("Line")
        self.add_dynamic_string_input("Line")

    def evaluate(self, context):
        lines = [f"exec({inp.python_value})" for inp in self.inputs[1:-1]]
        self.code = f"""
                    {self.indent(lines, 5)}
                    {self.indent(self.outputs[0].python_value, 5)}
                    """