import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_GetCustomPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetCustomPropertyNode"
    bl_label = "Get Custom Property"
    node_color = "PROPERTY"


    def on_create(self, context):
        self.add_property_input("Blend Data")
        self.add_string_input("Property")
        self.add_data_output("Property Value")


    def evaluate(self, context):
        if self.inputs[0].is_linked:
            self.outputs[0].python_value = f"{self.inputs[0].python_value}[{self.inputs[1].python_value}]"
        else:
            self.outputs[0].python_value = f""