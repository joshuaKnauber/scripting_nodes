import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PrintNode"
    bl_label = "Print"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_string_input()
        self.add_dynamic_string_input()
        self.add_execute_output()

    def evaluate(self, context):
        values = [inp.python_value for inp in self.inputs[1:-1]]
        self.code = f"""
                    print({", ".join(values)})
                    {self.indent(self.outputs[0].python_value, 5)}
                    """