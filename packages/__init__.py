import bpy


from . import package_operators


classes = [package_operators.SN_OT_InstallPackage,
            package_operators.SN_OT_UninstallPackage]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)