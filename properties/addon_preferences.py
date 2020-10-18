import bpy
import os
import json
import datetime
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
    addon_search: bpy.props.StringProperty(default="",name="Search")

    show_python_file: bpy.props.BoolProperty(default=False,name="Show Python File", description="Show python file in text editor after compiling")

    def update_check_frequency(self,context):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"update_log.json"), "r+" ,encoding="utf-8") as update_data:
            update_info = json.loads(update_data.read())
            update_info["update_frequency"] = self.update_frequency
            update_data.seek(0)
            update_data.write(json.dumps(update_info,indent=4))
            update_data.truncate()

    def update_seen_update(self,context):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"update_log.json"), "r+" ,encoding="utf-8") as update_data:
            update_info = json.loads(update_data.read())
            now = datetime.date.today()
            update_info["last_update"] = [now.day, now.month, now.year]
            update_data.seek(0)
            update_data.write(json.dumps(update_info,indent=4))
            update_data.truncate()

    do_update_notif: bpy.props.BoolProperty(default=True,name="Get Update Notifications", description="Get notifications when the addon has been updated")
    update_frequency: bpy.props.IntProperty(default=2,min=1,max=14,name="Days Between Check",description="The amount of days to wait before checking for updates", update=update_check_frequency)
    seen_new_update: bpy.props.BoolProperty(default=False,name="Seen Update",description="Don't show this notification again.",update=update_seen_update)

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
            with open(os.path.join(addon_folder,"installed_packages.json"), encoding="utf-8") as packages:
                installed_packages = json.load(packages)["packages"]

            for index, package in enumerate(installed_packages):
                self._draw_installed_package(package, index, layout)

            self._draw_install_package(layout)

    def draw_market_package(self,package, layout):
        box = layout.box()
        box.label(text=package.title)
        col = box.column(align=True)
        col.enabled = False
        for line in package.text.split(";;;"):
            col.label(text=line)
        row = box.row()
        row.scale_y = 1.25
        row.operator("wm.url_open",text=package.price).url = package.url


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
            col.separator()
            col.label(text="Settings")
            col.prop(self,"show_python_file")
            _row = col.row()
            _row.prop(self,"do_update_notif")
            _row = _row.row()
            _row.enabled = self.do_update_notif
            _row.prop(self,"update_frequency")

            col.separator()
            col.separator()
            col.label(text="Changelog 1.0.1")
            box = col.box()
            box.label(text="    • Added built in update notifications")
            box.label(text="    • Added 'Show In Search' option to button node")
            box.label(text="    • Added 'Show popups' option to run operator node")
            box.label(text="    • Added Multiply and Divide to Vector Math node")
            box.label(text="    • Added search to icon popup")
            box.label(text="    • Fixed encoding error when installing on some machines")

        elif self.main_nav == "PACKAGES":

            col = row.column()
            
            _row = col.row()
            split = _row.split(factor=0.5)
            split.label(text="Package Marketplace")
            _row = split.row(align=True)
            _row.operator("scripting_nodes.load_marketplace",icon="FILE_REFRESH",text="Load")
            _row.prop(self,"marketplace_search",text="",icon="VIEWZOOM")            
            _row.operator("wm.url_open",text="", icon="URL", emboss=False).url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/"

            if len(context.scene.sn_marketplace) == 1:
                box = col.box()
                box.enabled = False
                box.label(text="No packages found")
            elif len(context.scene.sn_marketplace) == 0:
                box = col.box()
                box.enabled = False
                box.label(text="Load the package marketplace first")                
            else:
                for package in context.scene.sn_marketplace:
                    if not package.title == "placeholder":
                        if self.marketplace_search in package.title or not self.marketplace_search:
                            self.draw_market_package(package,col)
                            
            col.separator()
            col.separator()
            self._draw_installed_packages(col)

        elif self.main_nav == "ADDONS":
            col = row.column()
            _row = col.row()
            split = _row.split(factor=0.5)
            split.label(text="Addon Marketplace")
            _row = split.row(align=True)
            _row.operator("scripting_nodes.load_addons",icon="FILE_REFRESH",text="Load")
            _row.prop(self,"addon_search",text="",icon="VIEWZOOM")
            
            if len(context.scene.sn_addons) == 1:
                box = col.box()
                box.enabled = False
                box.label(text="No addons found")
            elif len(context.scene.sn_addons) == 0:
                box = col.box()
                box.enabled = False
                box.label(text="Load the addon marketplace first")                
            else:
                for addon in context.scene.sn_addons:
                    if not addon.title == "placeholder":
                        if self.addon_search in addon.title or not self.addon_search:
                            self.draw_market_package(addon,col)


"""
Access:
addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
"""
