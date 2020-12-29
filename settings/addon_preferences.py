import bpy


class SN_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__.partition('.')[0]

    show_txt: bpy.props.BoolProperty(name="Show Python File",
                                    description="Shows the python file after compiling the addon",
                                    default=False)
    
    keep_after_error: bpy.props.BoolProperty(name="Keep File After Error",
                                    description="Keeps the python file after an error is encountered",
                                    default=False)
    
    use_suggestion_menu: bpy.props.BoolProperty(name="Use Suggestion Menu",
                                    description="Opens a menu with suggestions when draggin a link from a selected node and holding shift",
                                    default=True)

    check_for_updates: bpy.props.BoolProperty(name="Check For Updates",
                                    description="Checks for Serpens updates when opening blender",
                                    default=True)

    navigation: bpy.props.EnumProperty(items=[  ("DEV","Development","Development Preferences","NONE",0),
                                                ("SETTINGS","Settings","Serpens Settings","NONE",1),
                                                ("ADDONS","Addons","Serpens Addon Market","NONE",2),
                                                ("PACKAGES","Packages","Serpens Package Market","NONE",3)],
                                       name="SETTINGS",
                                       description="Navigation")


    def draw_dev_prefs(self,layout):
        pass


    def draw_serpens_settings(self,layout):
        row = layout.row()
        col = row.column()
        col.label(text="Development:")
        col.prop(self, "show_txt")
        col.prop(self, "keep_after_error")
        
        col = row.column()
        col.label(text="Node Editor:")
        col.prop(self, "use_suggestion_menu")
        
        col = row.column()
        col.label(text="Updates:")
        col.prop(self, "check_for_updates")


    def draw_addon_market(self,layout):
        pass
    
    
    def draw_package_market(self,layout):
        pass
        

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.2
        row.prop(self, "navigation", expand=True)
        if self.navigation == "DEV":
            self.draw_dev_prefs(layout)
        elif self.navigation == "SETTINGS":
            self.draw_serpens_settings(layout)
        elif self.navigation == "ADDONS":
            self.draw_addon_market(layout)
        elif self.navigation == "PACKAGES":
            self.draw_package_market(layout)
        
        
# addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences