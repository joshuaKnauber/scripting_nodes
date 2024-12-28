import bpy

ADDON_KEYMAPS = {}


def register_keymaps():
    global ADDON_KEYMAPS

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")

    # edit node group
    kmi = km.keymap_items.new(
        idname="sna.edit_group",
        type="TAB",
        value="PRESS",
        shift=False,
        ctrl=False,
        alt=False,
    )
    ADDON_KEYMAPS["edit_group"] = (km, kmi)

    # stop editing node group
    kmi = km.keymap_items.new(
        idname="sna.edit_group",
        type="TAB",
        value="PRESS",
        shift=False,
        ctrl=True,
        alt=False,
    )
    kmi.properties.always_quit = True
    ADDON_KEYMAPS["quit_group"] = (km, kmi)


def unregister_keymaps():
    global ADDON_KEYMAPS

    for key in ADDON_KEYMAPS:
        km, kmi = ADDON_KEYMAPS[key]
        km.keymap_items.remove(kmi)

    ADDON_KEYMAPS.clear()


def register():
    register_keymaps()


def unregister():
    unregister_keymaps()
