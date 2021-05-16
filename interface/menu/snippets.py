import bpy


class SN_MT_SnippetMenu(bpy.types.Menu):
    bl_idname = "SN_MT_SnippetMenu"
    bl_label = "Snippets"

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="test")


def snippet_menu(self, context):
    layout = self.layout
    row = layout.row()
    row.menu("SN_MT_SnippetMenu",text="test")