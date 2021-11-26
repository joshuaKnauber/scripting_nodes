import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_LabelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LabelNode"
    bl_label = "Label"

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")

    def evaluate(self, context):
        self.code = f"layout.label(text={self.inputs['Label'].python_value})"

    def draw_node(self, context, layout):
        pass