import bpy


class SN_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    check_for_updates: bpy.props.BoolProperty(name="Check For Updates",
                                            description="Check for updates online when loading the addon",
                                            default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "check_for_updates")

# addon_prefs = context.preferences.addons[bpy.context.scene.sn.addon_tree().sn_graphs[0].short()].preferences
