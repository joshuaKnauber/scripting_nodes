import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DisplayImageNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayImageNode"
    bl_label = "Display Image"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_icon_input("Icon")
        self.add_float_input("Scale").default_value = 1

    def evaluate(self, context):
        self.code = f"{self.active_layout}.template_icon(icon_value={self.inputs['Icon'].python_value}, scale={self.inputs['Scale'].python_value})"
