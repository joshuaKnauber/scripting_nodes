import bpy

from ..base_node import SN_BaseNode


class SN_PanelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PanelNode"
    bl_label = "Panel"

    def on_create(self):
        self.add_output("SN_InterfaceSocket", "Header")
        self.add_output("SN_InterfaceSocket", "Interface")

    def generate(self, context):
        sn = context.scene.sn
        self.code = f"""
class SNA_PT_Panel_{self.id}(bpy.types.Panel):
    bl_idname = "SNA_PT_Panel_{self.id}"
    bl_label = "My Panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"

    def draw(self, context):
        {self.outputs['Interface'].code(5, "pass")}
        """

        self.code_register = f"""
            bpy.utils.register_class(SNA_PT_Panel_{self.id})
        """

        self.code_unregister = f"""
            bpy.utils.unregister_class(SNA_PT_Panel_{self.id})
        """
