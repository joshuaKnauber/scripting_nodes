import bpy



class SN_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    navigation: bpy.props.EnumProperty(name="Navigation",
                                        description="Preferences Navigation",
                                        items=[("SETTINGS", "Settings", "Serpens settings", "PREFERENCES", 0),
                                                ("CUSTOM", "Custom", "Preview your addons preferences", "FILE_SCRIPT", 1)])

    check_for_updates: bpy.props.BoolProperty(name="Check For Updates",
                                        description="Check for updates online when loading the addon",
                                        default=True)


    def draw_serpens_prefs(self, context, layout):
        layout.prop(self, "check_for_updates")


    def draw_custom_prefs(self, context, layout):
        if context.scene.sn.preferences:
            context.scene.sn.preferences[0](layout)
        else:
            layout.label(text="No preferences node added to your addon.", icon="ERROR")


    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.2
        row.prop(self, "navigation", expand=True)

        if self.navigation == "SETTINGS":
            self.draw_serpens_prefs(context, layout)
        elif self.navigation == "CUSTOM":
            self.draw_custom_prefs(context, layout)



# addon_prefs = context.preferences.addons[bpy.context.scene.sn.addon_tree().sn_graphs[0].short()].preferences
