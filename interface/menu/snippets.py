import bpy
import os
import json


class SN_MT_SnippetMenu(bpy.types.Menu):
    bl_idname = "SN_MT_SnippetMenu"
    bl_label = "Snippets"

    def draw(self, context):
        layout = self.layout
        installed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "node_tree", "snippets", "installed.json")

        if hasattr(context, "snippet_category"):
            with open(installed_path, "r") as data:
                data = json.loads(data.read())
                file_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "node_tree", "snippets", "files")

                if not context.snippet_category:
                    for snippet in data["snippets"]:
                        op = layout.operator("sn.add_snippet_node", text=snippet["name"])
                        op.path = os.path.join(file_dir, snippet["filename"])

                else:
                    i = context.scene.sn.snippet_categories.find(context.snippet_category.name)
                    for snippet in data["categories"][i]["snippets"]:
                        op = layout.operator("sn.add_snippet_node", text=snippet["name"])
                        op.path = os.path.join(file_dir, snippet["filename"])


def snippet_menu(self, context):
    layout = self.layout

    for category in context.scene.sn.snippet_categories:
        row = layout.row()
        row.context_pointer_set("snippet_category", category)
        row.menu("SN_MT_SnippetMenu", text=category.name)

    if context.scene.sn.has_other_snippets:
        row = layout.row()
        row.context_pointer_set("snippet_category", None)
        row.menu("SN_MT_SnippetMenu", text="Others")