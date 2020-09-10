import bpy
import os
import json

class ScriptingNodesAddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    navigation: bpy.props.EnumProperty(items=[("PACKAGES","Packages","The place to manage your packages","PACKAGE",0),
                                            ("MARKETPLACE","Marketplace","The place to find new packages","IMAGE",1)])

    has_seen_tutorial: bpy.props.BoolProperty(default=False)
    has_seen_welcome_message: bpy.props.BoolProperty(default=False)

    def update_shortcuts(self,context):
        pass
    enable_compile_shortcut: bpy.props.BoolProperty(default=True,name="Use Compile Shortcut",description="You can use this shortcut to quickly recompile your addon",update=update_shortcuts)

    def _draw_install_package(self,layout):
        """ draws the button for installing packages """
        row = layout.row()
        row.scale_y = 1.5
        split = row.split(factor=0.5)
        split.operator("scripting_nodes.install_package",icon="PACKAGE")
        split.label(text="")

    def _draw_installed_package(self, package_data, index):
        """ draws the ui for an installed package """
        box = self.layout.box()
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

    def _draw_installed_packages(self):
        """ draws the list of installed packages """
        layout = self.layout
        layout.label(text="Installed packages:")
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
                self._draw_installed_package(package, index)

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

    def draw(self, context):
        row = self.layout.row(align=True)
        row.scale_y = 1.25
        row.prop(self,"navigation",text=" ",expand=True)
        self.layout.separator()

        if self.navigation == "PACKAGES":
            self._draw_installed_packages()

        elif self.navigation == "MARKETPLACE":

            self.layout.operator("scripting_nodes.load_marketplace",icon="FILE_REFRESH")
            for package in context.scene.sn_marketplace:
                self.draw_market_package(package)

"""
Access:
addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
"""
