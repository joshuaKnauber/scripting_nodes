import bpy
import os
import json

class ScriptingNodesAddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

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
        if bpy.context.scene.sn_properties.package_installed_without_reload:
            box = layout.box()
            box.alert = True
            box.label(text="Restart blender to reload the packages!")
        else:
            if bpy.context.scene.sn_properties.package_uninstalled_without_reload:
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

    def draw(self, context):
        self._draw_installed_packages()


"""
Access:
addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
"""
