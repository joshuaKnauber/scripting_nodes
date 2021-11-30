import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    bl_width_default = 200
    layout_type = "layout"
    is_trigger = True

    def on_create(self, context):
        self.add_interface_output()

    def evaluate(self, context):
        self.code = f"print({self.outputs[0].python_value})"

    def draw_node(self, context, layout):
        pass