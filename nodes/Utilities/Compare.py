import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_CompareNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CompareNode"
    bl_label = "Compare"
    node_color = "BOOLEAN"

    def on_create(self, context):
        self.add_data_input("Data")
        self.add_data_input("Data")
        self.add_boolean_output("Boolean")


    operation: bpy.props.EnumProperty(items=[("==", "=", "Equal"),
                                            ("!=", "≠", "Not equal"), 
                                            ("<", "<", "Smaller than"), 
                                            (">", ">", "Bigger than"), 
                                            ("<=", "≤", "Smaller or equal to"), 
                                            (">=", "≥", "Bigger or equal to")],
                                    name="Operation",
                                    description="Operation to perform on the input data",
                                    update=SN_ScriptingBaseNode._evaluate)


    def draw_node(self, context, layout):
        layout.prop(self, "operation", text='')

    def evaluate(self, context):
        self.outputs["Boolean"].python_value = f"({self.inputs[0].python_value} {self.operation} {self.inputs[1].python_value})"
