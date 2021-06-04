import bpy


from . import addon_preferences, addon_properties, load_markets, updates


classes = [addon_preferences.SN_AddonPreferences,
            addon_properties.SN_PackageDisplay,
            addon_properties.SN_AddonDisplay,
            addon_properties.SN_AddonProperties,
            load_markets.SN_OT_LoadAddons,
            load_markets.SN_OT_LoadPackages,
            updates.SN_OT_MessageUpdate]


def register():
    global classes
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)