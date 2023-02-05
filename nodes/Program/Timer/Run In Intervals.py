import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_RunInIntervalsNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RunInIntervalsNode"
    bl_label = "Run In Intervals"
    bl_width_default = 200
    node_color = "PROGRAM"

    def on_emergency_stop(self, context):
        if self.emergency_stop:
            if self.static_uid in bpy.context.scene.sn.function_store:
                bpy.app.timers.unregister(bpy.context.scene.sn.function_store[self.static_uid])
                del bpy.context.scene.sn.function_store[self.static_uid]
            self.emergency_stop = False

    emergency_stop: bpy.props.BoolProperty(default=False, update=on_emergency_stop)
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_float_input("Initial Delay").default_value = 1
        self.add_float_input("Interval Delay").default_value = 1
        self.add_boolean_input("Stop Condition").default_value = False
        self.add_execute_output("Interval")
        self.add_execute_output("Instant")

    def draw_node(self, context, layout):
        layout.prop(self, "emergency_stop", text="Manual Stop", toggle=True)

    def evaluate(self, context):
        self.code = f"""
                    def delayed_{self.static_uid}():
                        {self.indent(self.outputs['Interval'].python_value, 6) if self.outputs['Interval'].python_value.strip() else 'pass'}
                        if {self.inputs['Stop Condition'].python_value}:
                            return None
                        return {self.inputs['Interval Delay'].python_value}
                    
                    bpy.app.timers.register(delayed_{self.static_uid}, first_interval={self.inputs['Initial Delay'].python_value})
                    bpy.context.scene.sn.function_store["{self.static_uid}"] = delayed_{self.static_uid}

                    {self.indent(self.outputs['Instant'].python_value, 5)}
                    """
    
    def evaluate_export(self, context):
        self.code = f"""
                    def delayed_{self.static_uid}():
                        {self.indent(self.outputs['Interval'].python_value, 6) if self.outputs['Interval'].python_value.strip() else 'pass'}
                        if {self.inputs['Stop Condition'].python_value}:
                            return None
                        return {self.inputs['Interval Delay'].python_value}
                    
                    bpy.app.timers.register(delayed_{self.static_uid}, first_interval={self.inputs['Initial Delay'].python_value})

                    {self.indent(self.outputs['Instant'].python_value, 5)}
                    """