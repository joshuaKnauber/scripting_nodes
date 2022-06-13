import bpy
from ..keymaps.keymap import get_shortcut
from .preset_data import PresetData



class SN_PT_MarketFilters(bpy.types.Panel):
    bl_idname = "SN_PT_MarketFilters"
    bl_label = "Filter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout
        addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences
        layout.prop(addon_prefs, "only_serpens_3")



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
                                                ("SNIPPETS", "Snippets", "Get snippets made with and for Serpens"),
                                                ("ADDONS", "Addons", "Get addons made with Serpens")])

    check_for_updates: bpy.props.BoolProperty(name="Check For Updates",
                                        description="Check for updates online when loading the addon",
                                        default=True)

    use_colors: bpy.props.BoolProperty(name="Use Colored Nodes",
                                        description="Color nodes to match their category. Does not apply to existing nodes",
                                        default=True)
    
    keep_last_error_file: bpy.props.BoolProperty(name="Keep Error File",
                                        description="Keeps a copy of any compiled file that threw an error as 'serpens_error' in the text editor",
                                        default=False)
    
    search_addons: bpy.props.StringProperty(name="Search",
                                        description="Search through the loaded addons",
                                        options={"TEXTEDIT_UPDATE"})

    search_packages: bpy.props.StringProperty(name="Search",
                                        description="Search through the loaded packages",
                                        options={"TEXTEDIT_UPDATE"})

    search_snippets: bpy.props.StringProperty(name="Search",
                                        description="Search through the loaded snippets",
                                        options={"TEXTEDIT_UPDATE"})

    only_serpens_3: bpy.props.BoolProperty(name="Only Serpens 3",
                                        description="Hide all results from previous serpens versions")
    
    presets: bpy.props.CollectionProperty(name="Presets",
                                        description="Preset nodes",
                                        type=PresetData)


    def draw_serpens_prefs(self, context, layout):
        row = layout.row()

        col = row.column(heading="General")
        col.prop(self, "check_for_updates")
        col.prop(self, "use_colors")
        col.prop(get_shortcut("sn.force_compile"), "type", full_event=True, text="Force Compile")
        col.prop(get_shortcut("sn.open_node_docs"), "type", full_event=True, text="Node Docs")
        col.prop(get_shortcut("sn.add_copied_node"), "type", full_event=True, text="Add Node From Copied")
        
        col = row.column(heading="Debugging")
        col.prop(self, "keep_last_error_file")


    def draw_market_addon(self, addon_data):
        if not addon_data.name == "placeholder" and \
            (not self.only_serpens_3 or self.only_serpens_3 and addon_data.serpens_version == 3) and \
            (self.search_addons.lower() in addon_data.name.lower() or \
            self.search_addons.lower() in addon_data.description.lower() or \
            self.search_addons.lower() in addon_data.author.lower() or \
            self.search_addons.lower() in addon_data.category.lower()):
            box = self.layout.box()
            row = box.row()
            row.label(text=f"{addon_data.category}: {addon_data.name}")
            subrow = row.row()
            subrow.alignment = "RIGHT"
            subrow.label(text=addon_data.author)
            row = box.row()
            row.enabled = False
            row.label(text=addon_data.description)
            row = box.row()
            row.enabled = False
            row.label(text="Blender: " + ".".join(list(map(lambda i: str(i), list(addon_data.blender_version)))))
            row.label(text="Addon: " + ".".join(list(map(lambda i: str(i), list(addon_data.addon_version)))))
            row = box.row()
            row.operator("wm.url_open", text=addon_data.price if addon_data.price else "Free", icon="URL" if addon_data.is_external else "IMPORT").url = addon_data.addon_url
            if addon_data.has_blend:
                serpens_version = "" if addon_data.serpens_version == 3 else " (Serpens 2)"
                row.operator("wm.url_open", text=f"Download .blend{serpens_version}", icon="IMPORT").url = addon_data.blend_url
            return True
        return False


    def draw_market_package(self, package_data):
        if not package_data.name == "placeholder" and \
            (not self.only_serpens_3 or self.only_serpens_3 and package_data.serpens_version != 2) and \
            (self.search_packages.lower() in package_data.name.lower() or \
            self.search_packages.lower() in package_data.description.lower() or \
            self.search_packages.lower() in package_data.author.lower()):
            box = self.layout.box()
            row = box.row()
            row.label(text=package_data.name)
            subrow = row.row()
            subrow.alignment = "RIGHT"
            subrow.label(text=package_data.author)
            row = box.row()
            row.enabled = False
            row.label(text=package_data.description)
            serpens_version = "" if package_data.serpens_version != 2 else " (Serpens 2)"
            box.operator("wm.url_open", text=f"{package_data.price}{serpens_version}" if package_data.price else f"Free {serpens_version}", icon="URL").url = package_data.url
            return True
        return False


    def draw_market_snippet(self, snippet_data):
        if not snippet_data.name == "placeholder" and \
            (not self.only_serpens_3 or self.only_serpens_3 and snippet_data.serpens_version == 3) and \
            (self.search_snippets.lower() in snippet_data.name.lower() or \
            self.search_snippets.lower() in snippet_data.description.lower() or \
            self.search_snippets.lower() in snippet_data.author.lower()):
            box = self.layout.box()
            row = box.row()
            row.label(text=snippet_data.name)
            subrow = row.row()
            subrow.alignment = "RIGHT"
            subrow.label(text=snippet_data.author)
            row = box.row()
            row.enabled = False
            row.label(text=snippet_data.description)
            row = box.row()
            serpens_version = "" if snippet_data.serpens_version == 3 else " (Serpens 2)"
            row.operator("wm.url_open", text=f"{snippet_data.price}{serpens_version}" if snippet_data.price else f"Free {serpens_version}", icon="URL").url = snippet_data.url
            if snippet_data.blend_url:
                row.operator("wm.url_open", text=f"Download .blend{serpens_version}", icon="IMPORT").url = snippet_data.blend_url
            return True
        return False
        
        
    def draw_serpens_market(self, layout):
        sn = bpy.context.scene.sn
        row = layout.row()
        row.prop(self, "market_navigation", expand=True)
        row = layout.row()
        row.scale_y = 1
        found_results = False
        if self.market_navigation == "PACKAGES":
            found_results = not sn.packages
            if sn.packages:
                row.prop(self, "search_packages", text="", icon="VIEWZOOM")
                row.popover("SN_PT_MarketFilters", text="", icon="FILTER")
            row.operator("sn.load_packages", text="Load Packages" if not sn.packages else "Reload", icon="FILE_REFRESH")
            for package in sn.packages:
                found_results = self.draw_market_package(package) or found_results
        elif self.market_navigation == "SNIPPETS":
            found_results = not sn.snippets
            if sn.snippets:
                row.prop(self, "search_snippets", text="", icon="VIEWZOOM")
                row.popover("SN_PT_MarketFilters", text="", icon="FILTER")
            row.operator("sn.load_snippets", text="Load Snippets" if not sn.snippets else "Reload", icon="FILE_REFRESH")
            for snippet in sn.snippets:
                found_results = self.draw_market_snippet(snippet) or found_results
        elif self.market_navigation == "ADDONS":
            found_results = not sn.addons
            if sn.addons:
                row.prop(self, "search_addons", text="", icon="VIEWZOOM")
                row.popover("SN_PT_MarketFilters", text="", icon="FILTER")
            row.operator("sn.load_addons", text="Load Addons" if not sn.addons else "Reload", icon="FILE_REFRESH")
            for addon in sn.addons:
                found_results = self.draw_market_addon(addon) or found_results
        if not found_results:
            layout.label(text="No results found!")


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
