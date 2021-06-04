import bpy


from . import header


classes = [header.SN_PT_HeaderSettings]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)