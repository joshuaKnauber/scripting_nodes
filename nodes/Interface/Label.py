import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_LabelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LabelNode"
    bl_label = "Label"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")

    def evaluate(self, context):
        self.code = f"{self.active_layout}.label(text={self.inputs['Label'].python_value})"

    def draw_node(self, context, layout):
        pass