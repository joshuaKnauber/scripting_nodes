import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IfElseExecuteNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfElseExecuteNode"
    bl_label = "If/Else Execute"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_boolean_input("Condition")
        self.add_execute_output("Continue")
        self.add_execute_output("True")
        self.add_execute_output("False")

    def evaluate(self, context):
        self.code = f"""
                    if {self.inputs['Condition'].python_value}:
                        {self.outputs['True'].python_value if self.outputs['True'].python_value.strip() else 'pass'}
                    else:
                        {self.outputs['False'].python_value if self.outputs['True'].python_value.strip() else 'pass'}
                    {self.outputs['Continue'].python_value}
                    """