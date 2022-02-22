import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RepeatExecuteNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatExecuteNode"
    bl_label = "Loop Repeat (Execute)"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_integer_input("Repetitions").default_value = 2
        self.add_execute_output("Repeat")
        self.add_execute_output("Continue")
        self.add_integer_output("Step")

    def evaluate(self, context):
        self.outputs["Step"].python_value = f"i_{self.static_uid}"
        self.code = f"""
                    for i_{self.static_uid} in range({self.inputs['Repetitions'].python_value}):
                        {self.indent(self.outputs['Repeat'].python_value, 6) if self.outputs['Repeat'].python_value.strip() else 'pass'}
                    {self.indent(self.outputs['Continue'].python_value, 5)}
                    """