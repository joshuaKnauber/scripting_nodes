import bpy


from . import snippet_operators


classes = [snippet_operators.SN_OT_InstallSnippets,
            snippet_operators.SN_OT_UninstallSnippet,
            snippet_operators.SN_OT_UninstallSnippetCategory,
            snippet_operators.SN_OT_AddSnippetNode]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)