import bpy
import os
import json
from ..operators.keymaps.keymaps import register_keymaps, unregister_keymaps

class ScriptingNodesAddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    def update_nav(self,context):
        self.marketplace_search = ""

    navigation: bpy.props.EnumProperty(items=[("PACKAGES","Your Packages","The place to manage your packages","PACKAGE",0),
                                            ("MARKETPLACE","Marketplace","The place to find new packages","IMAGE",1),
                                            ("SETTINGS","Settings","Settings for the addon","PREFERENCES",2)],
                                        update = update_nav)

    def nav_items(self,context):
        return [("ADDON","","Serpens",bpy.context.scene.sn_icons[ "serpens" ].icon_id,0),
                ("PACKAGES","","Packages","PACKAGE",1),
                ("ADDONS","","Addons","ASSET_MANAGER",2)]

    main_nav: bpy.props.EnumProperty(items=nav_items)

    def update_seen_tutorial(self,context):
        if not self.tutorial_updated_self:
            context.scene.sn_properties.show_tutorial = True
        self.tutorial_updated_self = True

    tutorial_updated_self: bpy.props.BoolProperty(default=False)
    has_seen_tutorial: bpy.props.BoolProperty(default=False, update=update_seen_tutorial)

    marketplace_search: bpy.props.StringProperty(default="",name="Search")

    show_python_file: bpy.props.BoolProperty(default=False,name="Show Python File", description="Show python file in text editor after compiling")

    def _draw_install_package(self,layout):
        """ draws the button for installing packages """
        row = layout.row(align=True)
        split = row.split(factor=0.5)
        col = split.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("scripting_nodes.install_package",icon="PACKAGE")
        row.operator("wm.url_open",text="",icon="URL").url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/"
        split.label(text="")

    def _draw_installed_package(self, package_data, index, layout):
        """ draws the ui for an installed package """
        box = layoutt.box()
        row = box.row()
        split = row.split(factor=0.925)
        column = split.column(align=True)
        column.label(text=package_data["name"])
        column.label(text="By " + package_data["author"])
        row = column.row()
        row.enabled = False
        row.label(text=package_data["description"])
        row = split.row()
        row.scale_y = 3
        row.operator("scripting_nodes.uninstall_package",text="",icon="TRASH",emboss=False).package_index = index

    def _draw_installed_packages(self, layout):
        """ draws the list of installed packages """
        layout.label(text="Installed packages")
        if bpy.context.scene.sn_properties.package_installed_without_compile:
            box = layout.box()
            box.alert = True
            box.label(text="Restart blender to reload the packages!")
        else:
            if bpy.context.scene.sn_properties.package_uninstalled_without_compile:
                box = layout.box()
                box.alert = True
                box.label(text="Restart blender to reload the packages!")
            box = layout.box()
            column = box.column(align=True)
            column.label(text="Visual Scripting Basics")
            row = column.row()
            row.enabled = False
            row.label(text="The basic nodes to create addons")

            installed_packages = []
            addon_folder = os.path.dirname(os.path.dirname(__file__))
            with open(os.path.join(addon_folder,"installed_packages.json")) as packages:
                installed_packages = json.load(packages)["packages"]

            for index, package in enumerate(installed_packages):
                self._draw_installed_package(package, index, layout)

            self._draw_install_package(layout)

    def draw_market_package(self,package):
        box = self.layout.box()
        box.label(text=package.title)
        col = box.column(align=True)
        col.enabled = False
        for line in package.text.split(";;;"):
            col.label(text=line)
        row = box.row()
        row.scale_y = 1.25
        row.operator("wm.url_open",text=package.price).url = package.url

    # def draw(self, context):
    #     row = self.layout.row(align=True)
    #     row.scale_y = 1.25
    #     row.prop(self,"navigation",text=" ",expand=True)
    #     self.layout.separator()

    #     if self.navigation == "PACKAGES":

    #         row = self.layout.row(align=True)
    #         box = row.box()
    #         box.label(text="If you feel like a node or a feature is missing, let us know in discord!", icon="INFO")
    #         box = row.box()
    #         box.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id, emboss=False).url = "https://discord.com/invite/NK6kyae"

    #         self._draw_installed_packages()

    #     elif self.navigation == "MARKETPLACE":

    #         row = self.layout.row()
    #         split = row.split(factor=0.35)
    #         row = split.row(align=True)
    #         row.operator("scripting_nodes.load_marketplace",icon="FILE_REFRESH")
    #         row.operator("wm.url_open",text="", icon="URL").url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/"
    #         split.prop(self,"marketplace_search",text="",icon="VIEWZOOM")

    #         if len(context.scene.sn_marketplace) == 1:
    #             self.layout.label(text="No packages found")
    #         else:
    #             for package in context.scene.sn_marketplace:
    #                 if not package.title == "placeholder":
    #                     if self.marketplace_search in package.title or not self.marketplace_search:
    #                         self.draw_market_package(package)

    #     elif self.navigation == "SETTINGS":
    #         row = self.layout.row()
    #         row.prop(self,"show_python_file")


    def draw(self,context):
        row = self.layout.row()
        col = row.column()
        col.prop(self,"main_nav",expand=True,text=" ")
        col.scale_x = 1.5
        col.scale_y = 1.5
        
        if self.main_nav == "ADDON":
            col = row.column()
            _row = col.row(align=True)
            box = _row.box()
            box.label(text="If you feel like a node or a feature is missing, let us know on discord!", icon="INFO")
            box = _row.box()
            box.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id, emboss=False).url = "https://discord.com/invite/NK6kyae"
            
            col.separator()
            col.label(text="Settings")
            col.prop(self,"show_python_file")

        elif self.main_nav == "PACKAGES":

            col = row.column()
            self._draw_installed_packages(col)


"""
Access:
addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
"""
