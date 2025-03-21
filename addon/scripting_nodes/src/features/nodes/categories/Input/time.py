from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy



class SNA_Node_TimeNode(ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SNA_Node_TimeNode"
    bl_label = "Time and Date"

    def on_create(self):
        self.add_output("ScriptingStringSocket","Time")
        self.add_output("ScriptingIntegerSocket","Hours")
        self.add_output("ScriptingIntegerSocket","Minutes")
        self.add_output("ScriptingIntegerSocket","Seconds")
        self.add_output("ScriptingIntegerSocket","Milliseconds")
        self.add_output("ScriptingStringSocket","Date")
        self.add_output("ScriptingIntegerSocket","Year")
        self.add_output("ScriptingIntegerSocket","Month")
        self.add_output("ScriptingIntegerSocket","Day")


    def generate(self):
        self.code_global = f"from datetime import datetime"
        self.outputs[0].code = "str(datetime.now().time()).split(\".\")[0]"
        self.outputs[1].code = "datetime.now().time().hour"
        self.outputs[2].code = "datetime.now().time().minute"
        self.outputs[3].code = "datetime.now().time().second"
        self.outputs[4].code = "datetime.now().time().microsecond//1000"
        self.outputs[5].code = "str(datetime.now().date())"
        self.outputs[6].code = "datetime.now().date().year"
        self.outputs[7].code = "datetime.now().date().month"
        self.outputs[8].code = "datetime.now().date().day"
