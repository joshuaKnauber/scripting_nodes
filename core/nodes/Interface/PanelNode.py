import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_PanelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PanelNode"
    bl_label = "Panel"

    def on_create(self):
        self.add_output(sockets.INTERFACE, "Header")
        self.add_output(sockets.INTERFACE, "Interface")

    def generate(self, context):
        self.require_register = True
        self.code = f"""
class SNA_PT_Panel_{self.id}(bpy.types.Panel):
    bl_idname = "SNA_PT_Panel_{self.id}"
    bl_label = "My Panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"

    def draw_header(self, context):
        {self.outputs['Header'].get_code(5, "pass")}
        
    def draw(self, context):
        {self.outputs['Interface'].get_code(5, "pass")}
        """

        self.outputs["Header"].set_meta("layout", "self.layout")
        self.outputs["Interface"].set_meta("layout", "self.layout")
