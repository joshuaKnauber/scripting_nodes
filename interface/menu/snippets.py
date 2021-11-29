import bpy



class SN_MT_SnippetMenu(bpy.types.Menu):
    bl_idname = "SN_MT_SnippetMenu"
    bl_label = "Snippets"

    def draw(self, context):
        layout = self.layout
        # check old commits for explanation of context pointers



def snippet_menu(self, context):
    layout = self.layout