import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_TimeNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_TimeNode"
    bl_label = "Time and Date"
    node_color = "INTEGER"

    def on_create(self, context):
        self.add_string_output("Time")
        self.add_integer_output("Hours")
        self.add_integer_output("Minutes")
        self.add_integer_output("Seconds")
        self.add_integer_output("Milliseconds")
        self.add_string_output("Date")
        self.add_integer_output("Year")
        self.add_integer_output("Month")
        self.add_integer_output("Day")

    def evaluate(self, context):
        self.code_import = f"from datetime import datetime"
        self.outputs[0].python_value = "str(datetime.now().time()).split(\".\")[0]"
        self.outputs[1].python_value = "datetime.now().time().hour"
        self.outputs[2].python_value = "datetime.now().time().minute"
        self.outputs[3].python_value = "datetime.now().time().second"
        self.outputs[4].python_value = "datetime.now().time().microsecond//1000"
        self.outputs[5].python_value = "str(datetime.now().date())"
        self.outputs[6].python_value = "datetime.now().date().year"
        self.outputs[7].python_value = "datetime.now().date().month"
        self.outputs[8].python_value = "datetime.now().date().day"
