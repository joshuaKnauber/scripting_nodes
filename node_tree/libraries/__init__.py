import bpy


from . import load_snippet


classes = [load_snippet.SN_OT_LoadSnippet, ]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)
