import bpy


from . import header, menu, sidepanel


def register():
    header.register()
    menu.register()
    sidepanel.register()


def unregister():
    sidepanel.unregister()
    menu.unregister()
    header.unregister()