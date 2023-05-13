import bpy
from ...base_node import SN_BaseNode


class SN_PanelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PanelNode"
    bl_label = "Panel"

    def on_create(self, context):
        self.add_interface_output()
