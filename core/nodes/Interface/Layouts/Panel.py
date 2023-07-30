import bpy
from ...base_node import SN_BaseNode


class SN_PanelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PanelNode"
    bl_label = "Panel"

    def on_create(self, context):
        self.add_interface_output()

    def generate(self, context):
        sn = context.scene.sn
        self.code = f"""
            class {sn.info.short_identifier.upper()}_PT_Panel(bpy.types.Operator):
                bl_idname = "{sn.info.short_identifier.upper()}_PT_Panel"
                bl_label = "My Panel"
                bl_space_type = "NODE_EDITOR"
                bl_region_type = "UI"
                bl_category = "Serpens"

                def draw(self, context):
                    {self.outputs[0].code_block(5)}
        """
