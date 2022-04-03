import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RadiansNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RadiansNode"
    bl_label = "Convert Radians/Degrees"
    node_color = "FLOAT"

    def update_operation(self, context):
        if self.operation == "degrees":
            self.inputs[0].name = "Radians"
            self.outputs[0].name = "Degrees"
        else:
            self.inputs[0].name = "Degrees"
            self.outputs[0].name = "Radians"
        self._evaluate(context)

    operation: bpy.props.EnumProperty(items=[("degrees", "Radians to Degrees", "Convert Radians to Degrees"), ("radians", "Degrees to Radians", "Convert Degrees to radians")],name="Operation", update=update_operation)

    def on_create(self, context):
        self.add_float_input("Radians")
        self.add_float_output("Degrees")

    def draw_node(self, context, layout):
        layout.prop(self, "operation", text="")

    def evaluate(self, context):
        self.code_import = "import math"
        self.outputs[0].python_value = f"math.{self.operation}({self.inputs[0].python_value})"
