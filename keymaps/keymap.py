import bpy


#keymaps
addon_keymaps = {}


def get_shortcut(key):
    return addon_keymaps[key][1]


def register_keymaps():
    #registers the visual scripting keymaps

    #create keymap
    global addon_keymaps
    addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    
    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon
    kc = addon_keyconfig

    km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")

    # shortcut for recompiling
    # kmi = km.keymap_items.new(
    #     idname="wm.call_menu",
    #     type="A",
    #     value="PRESS",
    #     shift=True,
    #     ctrl=False,
    #     alt=False,
    #     )
    # kmi.properties.name = "SN_MT_AddNodeMenu"
    # addon_keymaps[ "compile" ] = (km, kmi)

    # shortcut for menu
    # kmi = km.keymap_items.new(
    #     idname="object.select_random",
    #     type="R",
    #     value="PRESS",
    #     shift=True,
    #     ctrl=False,
    #     alt=False,
    #     )
    # addon_keymaps[ "compile" ] = (km, kmi)


def unregister_keymaps():
    #unregister visual scripting keymaps
    global addon_keymaps

    for key in addon_keymaps:
        km, kmi = addon_keymaps[ key ]
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()