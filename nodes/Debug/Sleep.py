import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SleepNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_SleepNode"
    bl_label = "Sleep"
    bl_width_default = 200
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_float_input("Seconds")
        self.add_execute_output()

    def evaluate(self, context):
        self.code_import = "import time"
        self.code = f"""
            time.sleep({self.inputs[1].python_value})
            {self.indent(self.outputs[0].python_value, 3)}
        """