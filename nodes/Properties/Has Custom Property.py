import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_HasCustomPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_HasCustomPropertyNode"
    bl_label = "Has Custom Property"
    node_color = "PROPERTY"


    def on_create(self, context):
        self.add_property_input("Blend Data")
        self.add_string_input("Property")
        self.add_boolean_output("Property Exists")


    def evaluate(self, context):
        if self.inputs[0].links:
            self.outputs[0].python_value = f"{self.inputs[1].python_value} in {self.inputs[0].python_value}"
        else:
            self.outputs[0].python_value = f"False"