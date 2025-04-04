import bpy
from ....utils import normalize_code
from ...base_node import SN_ScriptingBaseNode



class SN_SetHeaderTextNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_SetHeaderTextNode"
    bl_label = "Set Header Text"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_property_input("Area")
        self.add_string_input("Text")
        self.add_boolean_input("Clear Text")
        
    def evaluate(self, context):
        self.code = f"""
        {self.inputs["Area"].python_value}.header_text_set(None if {self.inputs["Clear Text"].python_value} else {self.inputs["Text"].python_value})
        {self.indent(self.outputs[0].python_value, 2)}
        """