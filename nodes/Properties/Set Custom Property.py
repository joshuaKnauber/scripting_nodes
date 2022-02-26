import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SetCustomPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetCustomPropertyNode"
    bl_label = "Set Custom Property"
    node_color = "PROPERTY"


    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_property_input("Blend Data")
        self.add_string_input("Property")
        self.add_data_input("Property Value")


    def evaluate(self, context):
        if self.inputs[1].is_linked:
            self.code = f"""
                        {self.inputs[1].python_value}[{self.inputs[2].python_value}] = {self.inputs[3].python_value}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        else:
            self.code = f""