import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_TestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TestNode"
    bl_label = "Test Node"

    def on_create(self, context):
        self.add_string_input("String")

    def evaluate(self, context):
        print(self.inputs["String"].python_value, self.name)

    def draw_node(self, context, layout):
        layout.label(text=self.name)