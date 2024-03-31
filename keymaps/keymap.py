import bpy

from ..core.nodes.Group.operators.edit_operators import (
    SNA_OT_EditSerpensGroup,
    SNA_OT_MakeSerpensGroup,
    SNA_OT_QuitEditSerpensGroup,
)


# keymap store
addon_keymaps = {}


def register_keymaps():
    """Registers the visual scripting keymaps"""

    # create keymap
    global addon_keymaps

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")

    ### GROUP EDITING ###

    # shortcut for making a node group
    kmi = km.keymap_items.new(
        idname=SNA_OT_MakeSerpensGroup.bl_idname,
        type="G",
        value="PRESS",
        shift=False,
        ctrl=True,
        alt=False,
    )
    addon_keymaps["group"] = (km, kmi)

    # shortcut for editing a node group
    kmi = km.keymap_items.new(
        idname=SNA_OT_EditSerpensGroup.bl_idname,
        type="TAB",
        value="PRESS",
        shift=False,
        ctrl=False,
        alt=False,
    )
    addon_keymaps["group_edit"] = (km, kmi)

    # shortcut for stopping to edit a node group
    kmi = km.keymap_items.new(
        idname=SNA_OT_QuitEditSerpensGroup.bl_idname,
        type="TAB",
        value="PRESS",
        shift=False,
        ctrl=True,
        alt=False,
    )
    addon_keymaps["group_edit_stop"] = (km, kmi)


def unregister_keymaps():
    # unregister visual scripting keymaps
    global addon_keymaps

    for key in addon_keymaps:
        km, kmi = addon_keymaps[key]
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def get_shortcut(idname: str):
    """Returns the shortcut struct for the given idname"""
    # return bpy.context.window_manager.keyconfigs.user.keymaps[
    #     "Node Editor"
    # ].keymap_items[idname]
