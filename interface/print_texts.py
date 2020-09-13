import bpy
from ..compile.compiler import compiler


class SN_PT_PrintTextPanel(bpy.types.Panel):
    """Creates a panel for displaying print messages in the node editors sidebar"""
    bl_label = "Print Messages"
    bl_order = 2
    bl_idname = "SN_PT_PrintTextPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"

    @classmethod
    def poll(cls, context):
        return len(bpy.context.scene.sn_properties.print_texts) > 0

    def draw_header(self,context):
        self.layout.operator("scripting_nodes.clear_prints",icon="TRASH",text="")


    def draw(self, context):
        for text in bpy.context.scene.sn_properties.print_texts:
            self.layout.label(text=text.text)

