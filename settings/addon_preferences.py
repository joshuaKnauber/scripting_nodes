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
    
    
    addon_search: bpy.props.StringProperty(default="",name="Search")
    package_search: bpy.props.StringProperty(default="",name="Search")


    def draw_dev_prefs(self,layout):
        module = current_module()
        if module and "sn_draw_addon_prefs" in dir(module):
            module.sn_draw_addon_prefs(self)
        else:
            layout.label(text="No active addon preferences node",icon="QUESTION")
            


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
        
        
    def draw_package(self,layout,package):
        box = layout.box()
        row = box.row()
        subrow = row.row()
        subrow.scale_y = 1.2
        subrow.alignment = "LEFT"
        subrow.label(text=package.name)
        subrow = row.row()
        subrow.alignment = "RIGHT"
        subrow.enabled = False
        subrow.label(text=package.author)
        col = box.column(align=True)
        for line in package.description.split("\n"):
            col.label(text=line)
        box.operator("wm.url_open",text=package.price).url = package.url
    
    
    def draw_addon(self,layout,addon):
        box = layout.box()
        row = box.row()
        subrow = row.row()
        subrow.scale_y = 1.2
        subrow.alignment = "LEFT"
        subrow.prop(addon,"show_addon",text=addon.name,icon="DISCLOSURE_TRI_DOWN" if addon.show_addon else "DISCLOSURE_TRI_RIGHT",emboss=False)
        subrow = row.row()
        subrow.alignment = "RIGHT"
        subrow.enabled = False
        subrow.label(text=addon.category)
        if addon.show_addon:
            col = box.column(align=True)
            col.label(text="Description: ".ljust(15) + addon.description)
            col.label(text="Author: ".ljust(15) + addon.author)
            col.label(text="Version: ".ljust(15) + f"{addon.addon_version[0]}.{addon.addon_version[1]}.{addon.addon_version[2]}")
            col.label(text="Blender: ".ljust(15) + f"{addon.blender_version[0]}.{addon.blender_version[1]}.{addon.blender_version[2]}")
            row = col.row()
            row.operator("wm.url_open",text="Addon" if not addon.is_external else addon.price).url = addon.addon_url
            if addon.has_blend:
                row.operator("wm.url_open",text=".blend File").url = addon.blend_url
                


    def draw_addon_market(self,layout):
        addons = bpy.context.scene.sn.addons
        if not len(addons):
            row = layout.row()
            row.scale_y = 1.2
            row.operator("sn.load_addons", text="Load Addons", icon="FILE_REFRESH")
        elif len(addons) == 1:
            layout.label(text="There are no addons available just yet", icon="INFO")
        else:
            row = layout.row()
            row.prop(self,"addon_search",text="",icon="VIEWZOOM")
            row.operator("sn.load_addons",text="",emboss=False,icon="FILE_REFRESH")
            for addon in addons:
                if not addon.name == "placeholder":
                    if self.addon_search.lower() in addon.name.lower() or self.addon_search.lower() in addon.author.lower():
                        self.draw_addon(layout,addon)
    
    
    def draw_package_market(self,layout):
        packages = bpy.context.scene.sn.packages
        if not len(packages):
            row = layout.row()
            row.scale_y = 1.2
            row.operator("sn.load_packages", text="Load Packages", icon="FILE_REFRESH")
        elif len(packages) == 1:
            layout.label(text="There are no packages available just yet", icon="INFO")
        else:
            row = layout.row()
            row.prop(self,"package_search",text="",icon="VIEWZOOM")
            row.operator("sn.load_packages",text="",emboss=False,icon="FILE_REFRESH")
            for package in packages:
                if not package.name == "placeholder":
                    if self.package_search.lower() in package.name.lower() or self.package_search.lower() in package.author.lower():
                        self.draw_package(layout,package)
    
    
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