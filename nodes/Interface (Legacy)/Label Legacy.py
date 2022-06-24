import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_LabelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LabelNode"
    bl_label = "Label (Legacy)"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label").default_value = "My Label"
        self.add_icon_input("Icon")

    def evaluate(self, context):
        self.code = f"{self.active_layout}.label(text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})"

    def draw_node(self, context, layout):
        pass