import bpy
import os
from ...extensions import snippet_ops



class SN_MT_SnippetMenu(bpy.types.Menu):
    bl_idname = "SN_MT_SnippetMenu"
    bl_label = "Snippets"

    def draw(self, context):
        layout = self.layout
        
        if hasattr(context, "snippet"):
            for data in snippet_ops.loaded_snippets:
                if not type(data) == str and data["name"] == context.snippet.name:
                    for snippet in data["snippets"]:
                        layout.operator("sn.add_snippet", text=snippet.split(".")[0]).path = os.path.join(context.snippet.path, snippet)
        else:
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "packages", "snippets")
            for name in snippet_ops.loaded_snippets:
                if type(name) == str:
                    layout.operator("sn.add_snippet", text=name.split(".")[0]).path = os.path.join(path, name)



def snippet_menu(self, context):
    layout = self.layout
    no_cat_snippets = False
    for snippet in snippet_ops.loaded_snippets:
        if type(snippet) != str:
            row = layout.row()
            row.context_pointer_set("snippet", context.scene.sn.snippet_categories[snippet["name"]])
            row.menu("SN_MT_SnippetMenu", text=snippet["name"])
        else:
            no_cat_snippets = True
    if no_cat_snippets:
        layout.menu("SN_MT_SnippetMenu", text="Others")