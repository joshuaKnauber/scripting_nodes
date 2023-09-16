import bpy

from ..base_node import SN_BaseNode
from ..utils.references import NodePointer, node_search
from .PanelNode import SN_PanelNode


class SN_SubpanelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SubpanelNode"
    bl_label = "Subpanel"

    panel: bpy.props.PointerProperty(type=NodePointer, name="Panel", description="Panel to be displayed")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        node_search(layout, self.panel, SN_PanelNode.bl_idname)

    def on_create(self):
        self.add_output("SN_InterfaceSocket", "Header")
        self.add_output("SN_InterfaceSocket", "Interface")

    def generate(self, context):
        self.code = f"""
class SNA_PT_Panel_{self.id}(bpy.types.Panel):
    bl_idname = "SNA_PT_Panel_{self.id}"
    bl_label = "My Panel"
    bl_parent_id = ""
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"

    def draw_header(self, context):
        {self.outputs['Header'].code(5, "pass")}
        
    def draw(self, context):
        {self.outputs['Interface'].code(5, "pass")}
        """

        self.code_register = f"""
            bpy.utils.register_class(SNA_PT_Panel_{self.id})
        """

        self.code_unregister = f"""
            bpy.utils.unregister_class(SNA_PT_Panel_{self.id})
        """

        self.outputs["Header"].set_meta("layout", "self.layout")
        self.outputs["Interface"].set_meta("layout", "self.layout")
