import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_RunWithDelayNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RunWithDelayNode"
    bl_label = "Run With Delay"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_float_input("Delay").default_value = 1
        self.add_execute_output("Delayed")
        self.add_execute_output("Instant")

    def evaluate(self, context):
        self.code = f"""
                    def delayed_{self.static_uid}():
                        {self.indent(self.outputs['Delayed'].python_value, 6) if self.outputs['Delayed'].python_value.strip() else 'pass'}
                    
                    bpy.app.timers.register(delayed_{self.static_uid}, first_interval={self.inputs['Delay'].python_value})

                    {self.indent(self.outputs['Instant'].python_value, 5)}
                    """