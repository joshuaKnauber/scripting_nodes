import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_BooleanNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
    node_color = "BOOLEAN"

    def on_create(self, context):
        self.add_boolean_input("Boolean").set_hide(True)
        self.add_boolean_output("Boolean")

    def evaluate(self, context):
        self.outputs["Boolean"].python_value = self.inputs["Boolean"].python_value

    def draw_node(self, context, layout):
        layout.prop(self.inputs["Boolean"], "default_value", text="Value")