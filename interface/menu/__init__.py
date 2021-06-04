import bpy


from . import add_menu, rightclick, snippets


classes = [add_menu.SN_OT_RunAddMenu,
            add_menu.SN_OT_AddNode,
            add_menu.SN_MT_AddNodeSubMenu,
            add_menu.SN_MT_AddNodeMenu,
            rightclick.SN_OT_CopyProperty,
            rightclick.WM_MT_button_context,
            snippets.SN_MT_SnippetMenu]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)