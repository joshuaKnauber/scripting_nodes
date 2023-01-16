import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_StringNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_StringNode"
    bl_label = "String"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_input("String").set_hide(True)
        self.add_string_output("String")

    def evaluate(self, context):
        self.outputs["String"].python_value = self.inputs["String"].python_value

    def draw_node(self, context, layout):
        layout.prop(self.inputs["String"], "default_value", text="")