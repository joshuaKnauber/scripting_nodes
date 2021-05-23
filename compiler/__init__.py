import bpy

from . import compiler_ops, marketplace_ops


classes = [compiler_ops.SN_OT_Compile,
            compiler_ops.SN_OT_RemoveAddon,
            compiler_ops.SN_OT_ExportAddon,
            marketplace_ops.SN_OT_CopyCommand,
            marketplace_ops.SN_OT_ExportToMarketplaceAddon]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)