import bpy


from . import create_icons, icons_ui_list


classes = [create_icons.SN_OT_CreateIcon,
            create_icons.SN_OT_RemoveIcon,
            create_icons.SN_OT_AddGetIcon,
            create_icons.SN_OT_MoveIcon,
            icons_ui_list.SN_Icon,
            icons_ui_list.SN_UL_IconList]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)