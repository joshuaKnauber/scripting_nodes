import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_RunMultipleTimesNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RunMultipleTimesNode"
    bl_label = "Run Multiple Times"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_float_input("Initial Delay").default_value = 1
        self.add_float_input("Interval Delay").default_value = 1
        self.add_integer_input("Number of Times").default_value = 2
        self.add_execute_output("Delayed")
        self.add_execute_output("Instant")

    def evaluate(self, context):
        self.code_imperative = f"""
                    count_{self.static_uid} = 0
                    """

        self.code = f"""
                    global count_{self.static_uid}
                    count_{self.static_uid} = 0
                    
                    def delayed_{self.static_uid}():
                        global count_{self.static_uid}
                        {self.indent(self.outputs['Delayed'].python_value, 6) if self.outputs['Delayed'].python_value.strip() else 'pass'}
                        count_{self.static_uid} += 1
                        if count_{self.static_uid} >= {self.inputs['Number of Times'].python_value}:
                            return None
                        return {self.inputs['Interval Delay'].python_value}
                    
                    bpy.app.timers.register(delayed_{self.static_uid}, first_interval={self.inputs['Initial Delay'].python_value})

                    {self.indent(self.outputs['Instant'].python_value, 5)}
                    """