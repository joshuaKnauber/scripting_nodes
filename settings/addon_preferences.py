import bpy



class SN_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    navigation: bpy.props.EnumProperty(name="Navigation",
                                        description="Preferences Navigation",
                                        items=[("SETTINGS", "Settings", "Serpens settings", "PREFERENCES", 0),
                                                ("MARKET", "Marketplace", "Get things from the marketplace", "OUTLINER_OB_GROUP_INSTANCE", 1),
                                                ("CUSTOM", "Custom", "Preview your addons preferences", "FILE_SCRIPT", 2)])

    market_navigation: bpy.props.EnumProperty(name="Navigation",
                                        description="Marketplace Navigation",
                                        items=[("PACKAGES", "Packages", "Get packages for Serpens"),
                                                ("ADDONS", "Addons", "Get addons made with Serpens")])

    check_for_updates: bpy.props.BoolProperty(name="Check For Updates",
                                        description="Check for updates online when loading the addon",
                                        default=True)
    
    keep_last_error_file: bpy.props.BoolProperty(name="Keep Error File",
                                        description="Keeps a copy of any compiled file that threw an error as 'serpens_error' in the text editor",
                                        default=False)


    def draw_serpens_prefs(self, context, layout):
        row = layout.row()

        col = row.column(heading="General")
        col.prop(self, "check_for_updates")
        
        col = row.column(heading="Debugging")
        col.prop(self, "keep_last_error_file")
        
        
    def draw_serpens_market(self, layout):
        row = layout.row()
        row.prop(self, "market_navigation", expand=True)


    def draw_custom_prefs(self, context, layout):
        if context.scene.sn.preferences:
            layout.label(text="This will be shown in your preferences:", icon="INFO")
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
        if self.navigation == "MARKET":
            self.draw_serpens_market(layout)
        elif self.navigation == "CUSTOM":
            self.draw_custom_prefs(context, layout)



# addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
