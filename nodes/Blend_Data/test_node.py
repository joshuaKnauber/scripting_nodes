import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_TestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TestNode"
    bl_label = "Test Node"

    def on_create(self, context):
        self.add_string_input()
        self.add_string_output()

    def evaluate(self, context):
        pass

    def draw_node(self, context, layout):
        layout.label(text=self.inputs[0].default_value)