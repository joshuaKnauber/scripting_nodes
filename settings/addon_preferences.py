import bpy
from .. import bl_info
from ..compiler.compiler import current_module


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
    
    show_all_compatible: bpy.props.BoolProperty(name="Show All Compatible",
                                    description="Shows all compatible nodes instead of only those with the same socket type",
                                    default=False)

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
        module = current_module()
        if module and "sn_draw_addon_prefs" in dir(module):
            module.sn_draw_addon_prefs(self)
        else:
            layout.label(text="No active addon preferences node",icon="ERROR")
            


    def draw_serpens_settings(self,layout):
        row = layout.row()
        col = row.column()
        col.label(text="Development:")
        col.prop(self, "show_txt")
        col.prop(self, "keep_after_error")
        
        col = row.column()
        col.label(text="Node Editor:")
        col.prop(self, "use_suggestion_menu")
        subrow = col.row()
        subrow.enabled = self.use_suggestion_menu
        subrow.prop(self, "show_all_compatible")
        
        col = row.column()
        col.label(text="Updates:")
        col.prop(self, "check_for_updates")


    def draw_addon_market(self,layout):
        pass
    
    
    def draw_package_market(self,layout):
        pass
    
    
    def draw_navigation(self,layout):
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.prop_enum(self,"navigation",value="DEV")
        row.separator()
        row.prop_enum(self,"navigation",value="SETTINGS")
        row.prop_enum(self,"navigation",value="ADDONS")
        row.prop_enum(self,"navigation",value="PACKAGES")


    def draw_changelog(self,layout):
        changelog = [
            "Rewrite of the entire addon",
            "Added multiple node trees for one addon",
            "Separated Properties and Variables",
            "Added custom icons",
            "Export as .zip file to allow for addon assets",
            "And much more..."
        ]
        if changelog:
            box = layout.box()
            version = str(bl_info['version'])[1:-1].replace(",",".").replace(" ","")
            box.label(text=f"Changelog for v{version}:")
            col = box.column(align=True)
            col.enabled = False
            for entry in changelog:
                col.label(text="   • " + entry)
        

    def draw(self, context):
        layout = self.layout
        self.draw_navigation(layout)
        if self.navigation == "DEV":
            self.draw_dev_prefs(layout)
        elif self.navigation == "SETTINGS":
            self.draw_serpens_settings(layout)
            self.draw_changelog(layout)
        elif self.navigation == "ADDONS":
            self.draw_addon_market(layout)
        elif self.navigation == "PACKAGES":
            self.draw_package_market(layout)
        
        
# addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences