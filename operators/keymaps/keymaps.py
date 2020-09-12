import bpy


#keymaps
addon_keymaps = {}

def get_shortcut(key):
    return addon_keymaps[key][1]

def draw_keymaps( layout ):
    """ draws the keymap settings for the preferences """
    global addon_keymaps
    addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences

    box = layout.box()
    box.prop( addon_prefs, "enable_compile_shortcut" )
    if "compile" in addon_keymaps:
        kmi = addon_keymaps[ "compile" ][1]
        row = box.row()
        row.enabled = addon_prefs.enable_compile_shortcut
        row.prop( kmi, "type", text="", full_event=True )


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
    if addon_prefs.enable_compile_shortcut:
        kmi = km.keymap_items.new(
            idname="scripting_nodes.compile_active",
            type="R",
            value="PRESS",
            shift=True,
            ctrl=False,
            alt=False,
            )
        addon_keymaps[ "compile" ] = (km, kmi)


def unregister_keymaps():
    #unregister layer painter keymaps
    global addon_keymaps

    for key in addon_keymaps:
        km, kmi = addon_keymaps[ key ]
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()