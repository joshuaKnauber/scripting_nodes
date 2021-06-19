import bpy
import os
import json
from .. import bl_info


class SN_AddonPreferences(bpy.types.AddonPreferences):
    
    bl_idname = __name__.partition('.')[0]

    show_txt: bpy.props.BoolProperty(name="Show Python File",
                                    description="Shows the python file after compiling the addon",
                                    default=False)
    
    keep_after_error: bpy.props.BoolProperty(name="Keep File After Error",
                                    description="Keeps the python file after an error is encountered",
                                    default=False)
    
    use_suggestion_menu: bpy.props.BoolProperty(name="Use Suggestion Menu",
                                    description="When enabled, you can drag and drop a link from a socket in the node editor while holding Shift to open a menu of compatible nodes (only works on monitors with the scale set to 100%)",
                                    default=True)
    
    show_all_compatible: bpy.props.BoolProperty(name="Show All Compatible",
                                    description="Shows all compatible nodes instead of only those with the same socket type",
                                    default=False)

    check_for_updates: bpy.props.BoolProperty(name="Check For Updates",
                                    description="Checks for Serpens updates when opening blender",
                                    default=True)
    
    show_full_errors: bpy.props.BoolProperty(name="Show Full Errors",
                                             description="Show the full error messages in the console",
                                             default=False)
    
    no_zip_export: bpy.props.BoolProperty(name="Export Unzipped",
                                             description="Exports your addon without zipping it",
                                             default=False)
    
    debug_export: bpy.props.BoolProperty(name="Debug Export",
                                             description="Prints debug messages for the export process",
                                             default=False)

    navigation: bpy.props.EnumProperty(items=[  ("SETTINGS","Settings","Serpens Settings","NONE",1),
                                                ("ADDONS","Addons","Serpens Addon Market","NONE",2),
                                                ("PACKAGES","Packages","Serpens Package Market","NONE",3),
                                                ("SNIPPETS","Snippets","Serpens Snippets","NONE",4)],
                                       default = "SETTINGS",
                                       name="SETTINGS",
                                       description="Navigation")
    
    
    addon_search: bpy.props.StringProperty(default="",name="Search",options={"TEXTEDIT_UPDATE"})
    package_search: bpy.props.StringProperty(default="",name="Search",options={"TEXTEDIT_UPDATE"})



    def draw_serpens_settings(self,layout):
        row = layout.row()        
        col = row.column()
        col.label(text="Node Editor:")
        col.prop(self, "use_suggestion_menu")
        subrow = col.row()
        subrow.enabled = self.use_suggestion_menu
        subrow.prop(self, "show_all_compatible")
        
        col = row.column()
        col.label(text="Debugging:")
        col.prop(self, "show_full_errors")
        col.prop(self, "show_txt")
        col.prop(self, "keep_after_error")
        col.prop(self, "no_zip_export")
        col.prop(self, "debug_export")
        
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
            col.separator()
            row = col.row()
            row.operator("wm.url_open",text="Download Addon" if not addon.is_external else addon.price).url = addon.addon_url
            if addon.has_blend:
                row.operator("wm.url_open",text="Download .blend").url = addon.blend_url
                

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
                        
                        
    def draw_installed(self,layout):
        installed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"packages","installed.json")
        has_installed = False
        with open(installed_path) as installed:
            for index, package in enumerate(json.loads(installed.read())["packages"]):
                has_installed = True
                box = layout.box()
                row = box.row()
                subrow = row.row()
                subrow.scale_y = 1.2
                subrow.alignment = "LEFT"
                subrow.label(text=package["name"])
                subrow = row.row()
                subrow.alignment = "RIGHT"
                v = package["package_version"]
                subrow.label(text=f"{v[0]}.{v[1]}.{v[2]}")
                subrow.operator("sn.uninstall_package",text="",icon="X",emboss=False).index = index
                col = box.column(align=True)
                col.label(text="Description: ".ljust(15) + package["description"])
                col.label(text="Author: ".ljust(16) + package["author"])
                if package["wiki_url"]:
                    col.label(text="Wiki: ".ljust(18) + package["wiki_url"])
                col.separator()
                if not list(bl_info["version"]) in package["serpens_versions"] and len(package["serpens_versions"]):
                    row = col.row()
                    row.alert = True
                    row.label(text="This package doesn't officially support this Serpens version.",icon="INFO")
                    row = col.row()
                    row.alert = True
                    row.label(text="There might be issues with these nodes.",icon="BLANK1")
                
        if not has_installed:
            layout.label(text="You don't have any installed packages", icon="INFO")
    
    
    def draw_package_market(self,layout):
        packages = bpy.context.scene.sn.packages
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("sn.install_package",text="Install Package",icon="IMPORT")
        self.draw_installed(layout)
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


    def draw_snippets(self,layout):
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("sn.install_snippets",text="Install Snippets",icon="IMPORT")

        installed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"node_tree","snippets","installed.json")
        with open(installed_path) as installed:
            data = json.loads(installed.read())
            for cIndex, category in enumerate(data["categories"]):
                box = layout.box()
                row = box.row()
                row.label(text=category["name"])
                row.operator("sn.uninstall_snippet_category",text="",icon="TRASH",emboss=False)

                col = box.column(align=True)
                for i, snippet in enumerate(category["snippets"]):
                    row = col.row()
                    subcol = row.column()
                    subcol.enabled = False
                    subcol.label(text=snippet["name"])
                    op = row.operator("sn.uninstall_snippet",text="",icon="X",emboss=False)
                    op.has_category = True
                    op.categoryIndex = cIndex
                    op.snippetIndex = i

            if len(data["snippets"]) > 0:
                box = layout.box()
                for i, snippet in enumerate(data["snippets"]):
                    row = box.row()
                    row.label(text=snippet["name"])
                    op = row.operator("sn.uninstall_snippet",text="",icon="X",emboss=False)
                    op.has_category = False
                    op.snippetIndex = i

            if len(data["categories"]) + len(data["snippets"]) == 0:
                layout.label(text="No snippets installed. Export snippets in the N-Panel",icon="INFO")

            
    
    
    def draw_navigation(self,layout):
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.prop(self,"navigation",expand=True)


    def draw_changelog(self,layout):
        changelog = [
            "Temporary work around for blender bug T88986 (operator properties)",
            "Fixed Is Export property and node",
            "Fixed drag add menu with node frames",
            "Added toggle system console button in header settings",
            "Added screen output to scene context node",
            "Use blender auto save as default for serpens auto save",
            "Show message about status of auto save when creating addon",
            "Fixed property nodes for custom properties like geo-nodes",
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
        if self.navigation == "SETTINGS":
            self.draw_serpens_settings(layout)
            self.draw_changelog(layout)
        elif self.navigation == "ADDONS":
            self.draw_addon_market(layout)
        elif self.navigation == "PACKAGES":
            self.draw_package_market(layout)
        elif self.navigation == "SNIPPETS":
            self.draw_snippets(layout)
        
        
# addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences