import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SetPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_SetPropertyNode"
    bl_label = "Set Property"
    node_color = "PROPERTY"


    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("Property")
        self.add_data_input("Value").changeable = True
        self.add_execute_output()


    def evaluate(self, context):
        if self.inputs[1].is_linked:
            self.code = f"""
                        {self.inputs[1].python_value} = {self.inputs[2].python_value}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
        else:
            self.code = f"""
                        {self.indent(self.outputs[0].python_value, 6)}
                        """