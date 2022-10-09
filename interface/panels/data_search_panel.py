import bpy
from ...addon.properties.settings.settings import property_icons
from ...settings.data_properties import filter_defaults
from ...settings import global_search
        
        
        
class SN_PT_navigation_bar(bpy.types.Panel):
    bl_label = "Preferences Navigation"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sn.hide_preferences

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        row = layout.row()
        row.scale_y = 1.4
        row.alert = True
        row.operator("sn.exit_search", text="Exit", icon="PANEL_CLOSE")

        layout.separator()
        layout.operator("wm.url_open", text="How to", icon="QUESTION").url = "https://joshuaknauber.notion.site/Blend-Data-33e9f2ea40f44c2498cb26838662b621"

        layout.separator(factor=2)
        col = layout.column(align=True)
        col.scale_y = 1.4
        col.operator("sn.reload_data", text="Reload", icon="FILE_REFRESH")
        col.separator()
        col.prop_enum(sn, "data_category", value="discover", icon="WORLD")

        layout.separator()
        layout.label(text="Source:")
        col = layout.column(align=True)
        col.scale_y = 1.4
        col.prop_enum(sn, "data_category", value="app")
        col.prop_enum(sn, "data_category", value="context")
        col.prop_enum(sn, "data_category", value="data")
        col.separator()
        col.prop_enum(sn, "data_category", value="ops")

        layout.separator()
        col = layout.column()
        row = col.row()
        row.label(text="Filter Overview:")
        row.operator("sn.reset_filters", text="", icon="LOOP_BACK", emboss=False)

        if sn.data_category == "discover":
            row = col.row()
            row.enabled = False
            row.label(text=f"Total: {len(global_search.data_flat)} items")
            row = col.row()
            row.enabled = False
            row.label(text=f"Full Matches: {sn.discover_data['full_matches']} items")
            
        row = col.row()
        row.scale_y = 1.2
        if sn.data_category == "discover":
            row.prop(sn, "discover_search", text="", icon="VIEWZOOM")
        else:
            row.prop(sn, "data_search", text="", icon="VIEWZOOM")
        subcol = col.column()
        subcol.enabled = sn.data_category != "ops"
        subcol.prop(sn, "data_filter", expand=True)
        
        layout.separator()
        layout.prop(sn, "show_path")
        if sn.data_category == "discover":
            layout.prop(sn, "discover_full_only")
            layout.prop(sn, "discover_show_amount")
        
        
        
class SN_PT_FilterDataSettings(bpy.types.Panel):
    bl_idname = "SN_PT_FilterDataSettings"
    bl_label = "Filter"
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        if getattr(context, "sn_filter_path", None):
            row = layout.row()
            row.prop(context.sn_filter_path, "data_search", text="", icon="VIEWZOOM")
            col = layout.column()
            col.prop(context.sn_filter_path, "data_filter")



path_notes = {
    "bpy.context.preferences.keymap": "Copy shortcuts from Context -> Window Manager -> Keyconfigs -> Your Shortcut -> Type",
    "bpy.context.window_manager.keyconfigs": "To display a shortcut, find it in the User Key Config below, copy its Type property and check Full Shortcut on the node",
    "bpy.context.active_object": "To set the active object use the active object output on the Objects node or copy the active object from the active view layer",
}

class SN_PT_data_search(bpy.types.Panel):
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_label = "Display"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.sn.hide_preferences
    
    def should_draw(self, item, search_value, filters):
        if search_value.lower() in item["name"].lower():
            return item["type"] in filters
        return False
    
    def draw_item(self, layout, item):
        box = layout.box()
        row = box.row()
        
        if not item["has_properties"]:
            row.scale_y = 0.75
        else:
            op = row.operator("sn.expand_data", text="", icon="TRIA_DOWN" if item["expanded"] else "TRIA_RIGHT", emboss=False)
            op.path = item["path"]

            subrow = row.row(align=True)
            has_filters = item["data_search"] != "" or item["data_filter"] != filter_defaults
            op = subrow.operator("sn.filter_data", text="", icon="FILTER", emboss=has_filters, depress=has_filters)
            op.path = item["path"]
            if has_filters:
                op = subrow.operator("sn.reset_item_filters", text="", icon="LOOP_BACK", depress=True)
                op.path = item["path"]

        row.label(text=item["name"])
        
        icon = property_icons[item["type"]] if item["type"] in property_icons else "ERROR"
        subrow = row.row()
        subrow.enabled = False
        subrow.label(text=item["type"], icon=icon)

        if bpy.context.scene.sn.show_path:
            subrow = row.row()
            subrow.enabled = False
            subrow.label(text=item["path"])
        
        if item["has_properties"]:
            op = row.operator("sn.reload_item_data", text="", icon="FILE_REFRESH", emboss=False)
            op.path = item["path"]

        op = row.operator("sn.copy_data_path", text="", icon="COPYDOWN", emboss=False)
        op.path = item["path"]
        op.type = item["type"]
        op.required = item["required"]
        
        if item["expanded"]:
            row = box.row()
            split = row.split(factor=0.015)
            split.label(text="")
            col = split.column(align=True)
                
            if item["path"] in path_notes:
                box = col.box()
                box.scale_y = 0.75
                box.label(text=path_notes[item["path"]], icon="INFO")
            
            is_empty = True
            for key in item["properties"].keys():
                sub_item = item["properties"][key]
                if self.should_draw(sub_item, item["data_search"], item["data_filter"]):
                    self.draw_item(col, sub_item)
                    if sub_item["clamped"]:
                        box = col.box()
                        box.scale_y = 0.75
                        box.label(text="... Shortened because of too many items", icon="PLUS")
                        col.separator()
                    is_empty = False

            if is_empty:
                col.label(text="No Items for these filters!", icon="INFO")

    def draw_operator_category(self, layout, category):
        sn = bpy.context.scene.sn

        box = layout.box()
        row = box.row()
        op = row.operator("sn.expand_data", text="", icon="TRIA_DOWN" if sn.ops_items["operators"][category]["expanded"] else "TRIA_RIGHT", emboss=False)
        op.path = f"bpy.ops.{category}"
        if category == "sn":
            row.label(text="Serpens")
        elif category == "sna":
            row.label(text="Serpens Addon")
        else:
            row.label(text=category.replace("_", " ").title())

        if sn.ops_items["operators"][category]["expanded"]:
            row = box.row()
            split = row.split(factor=0.015)
            split.label(text="")
            col = split.column(align=True)

            for operator in sn.ops_items["operators"][category]["items"]:
                if operator["operator"] in sn.ops_items["filtered"][category]:
                    path = f"bpy.ops.{category}.{operator['operator']}()"
                    box = col.box()
                    box.scale_y = 0.75
                    row = box.row()
                    row.label(text=operator["name"])

                    if bpy.context.scene.sn.show_path:
                        subrow = row.row()
                        subrow.enabled = False
                        subrow.label(text=path)

                    op = row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False)
                    op.name = path

    def draw_global_search(self, layout):
        sn = bpy.context.scene.sn

        def is_section_in_search(section):
            if sn.discover_search.startswith(section) or \
                sn.discover_search.endswith(section) or \
                f",{section}," in sn.discover_search:
                return True
            return False

        col = layout.column(align=True)
        for path in bpy.context.scene.sn.discover_data["items"]:
            item = global_search.data_flat[path]

            box = col.box()
            row = box.row()

            subrow = row.row(align=True)
            subrow.alignment = "LEFT"
            for section in path.split("."):
                if not section == "bpy":
                    display = section.replace("_", " ").title()
                    if "[" in display and "]" in display:
                        display = display.split("[")[0] + ": " + display.split("[")[1].replace("]", "")
                    subrow.operator("sn.add_to_search", text=display, emboss=not is_section_in_search(section)).section = section

            row.label(text="")

            if bpy.context.scene.sn.show_path:
                subcol = row.column()
                subcol.enabled = False
                subcol.label(text=path)
                
            row.label(text="")

            op = row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False)
            op.name = path

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        col = layout.column(align=True)

        if sn.data_category == "discover":
            self.draw_global_search(col)

        else:
            is_empty = True
            if sn.data_category == "ops":
                row = col.row()
                row.label(text="Use property functions instead of operators when possible!", icon="INFO")
                row.operator("sn.expand_operators", text="", icon="FULLSCREEN_ENTER", emboss=False)
                col.separator()
                for cat in sn.ops_items["operators"].keys():
                    if cat in sn.ops_items["filtered"].keys():
                        self.draw_operator_category(col, cat)
                        is_empty = False
            else:
                for key in sn.data_items[sn.data_category].keys():
                    item = sn.data_items[sn.data_category][key]
                    if self.should_draw(item, sn.data_search, sn.data_filter):
                        self.draw_item(col, item)
                        is_empty = False
                        
            if is_empty:
                layout.label(text="No Items for these filters!", icon="INFO")