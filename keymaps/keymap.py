import bpy


# keymaps
addon_keymaps = {}


def get_shortcut(idname):
    """ Returns the shortcut struct for the given idname """
    return bpy.context.window_manager.keyconfigs.user.keymaps["Node Editor"].keymap_items[idname]


def register_keymaps():
    # registers the visual scripting keymaps

    # create keymap
    global addon_keymaps
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")

    # shortcut for compiling
    kmi = km.keymap_items.new(
        idname="sn.force_compile",
        type="R",
        value="PRESS",
        shift=True,
        ctrl=False,
        alt=False,
        )
    addon_keymaps["compile"] = (km, kmi)

    # shortcut for docs
    kmi = km.keymap_items.new(
        idname="sn.open_node_docs",
        type="F1",
        value="PRESS",
        shift=False,
        ctrl=False,
        alt=False,
        )
    addon_keymaps["docs"] = (km, kmi)

    # shortcut for adding a blend property
    kmi = km.keymap_items.new(
        idname="sn.add_blend_property",
        type="V",
        value="PRESS",
        shift=True,
        ctrl=False,
        alt=False,
        )
    addon_keymaps["docs"] = (km, kmi)


def unregister_keymaps():
    # unregister visual scripting keymaps
    global addon_keymaps

    for key in addon_keymaps:
        km, kmi = addon_keymaps[ key ]
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()