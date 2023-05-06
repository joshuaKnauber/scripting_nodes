import bpy


# keymaps
addon_keymaps = {}


def get_shortcut(idname):
    """Returns the shortcut struct for the given idname"""
    return bpy.context.window_manager.keyconfigs.user.keymaps[
        "Node Editor"
    ].keymap_items[idname]


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

    # shortcut for making a node group
    kmi = km.keymap_items.new(
        idname="sn.make_serpens_group",
        type="G",
        value="PRESS",
        shift=False,
        ctrl=True,
        alt=False,
    )
    addon_keymaps["group"] = (km, kmi)

    # shortcut for editing a node group
    kmi = km.keymap_items.new(
        idname="sn.edit_serpens_node_group",
        type="TAB",
        value="PRESS",
        shift=False,
        ctrl=False,
        alt=False,
    )
    addon_keymaps["group_edit"] = (km, kmi)

    # shortcut for stopping to edit a node group
    kmi = km.keymap_items.new(
        idname="sn.quit_edit_serpens_node_group",
        type="TAB",
        value="PRESS",
        shift=False,
        ctrl=True,
        alt=False,
    )
    addon_keymaps["group_edit_stop"] = (km, kmi)

    # shortcut for adding a node from copied path
    kmi = km.keymap_items.new(
        idname="sn.add_copied_node",
        type="V",
        value="PRESS",
        shift=True,
        ctrl=False,
        alt=False,
    )
    addon_keymaps["copied"] = (km, kmi)


def unregister_keymaps():
    # unregister visual scripting keymaps
    global addon_keymaps

    for key in addon_keymaps:
        km, kmi = addon_keymaps[key]
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
